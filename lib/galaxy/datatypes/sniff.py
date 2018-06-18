"""
File format detector
"""
from __future__ import absolute_import

import codecs
import gzip
import logging
import os
import re
import shutil
import sys
import tempfile
import zipfile

from six import StringIO, text_type
from six.moves import filter
from six.moves.urllib.request import urlopen

from galaxy import util
from galaxy.util import compression_utils
from galaxy.util.checkers import (
    check_binary,
    check_bz2,
    check_gzip,
    check_html,
    check_zip,
    is_tar,
)

if sys.version_info < (3, 3):
    import bz2file as bz2
else:
    import bz2

log = logging.getLogger(__name__)

SNIFF_PREFIX_BYTES = int(os.environ.get("GALAXY_SNIFF_PREFIX_BYTES", None) or 2 ** 20)


def get_test_fname(fname):
    """Returns test data filename"""
    path, name = os.path.split(__file__)
    full_path = os.path.join(path, 'test', fname)
    return full_path


def stream_url_to_file(path):
    page = urlopen(path)  # page will be .close()ed in stream_to_file
    temp_name = stream_to_file(page, prefix='url_paste', source_encoding=util.get_charset_from_http_headers(page.headers))
    return temp_name


def stream_to_open_named_file(stream, fd, filename, source_encoding=None, source_error='strict', target_encoding=None, target_error='strict'):
    """Writes a stream to the provided file descriptor, returns the file name. Closes file descriptor"""
    # signature and behavor is somewhat odd, due to backwards compatibility, but this can/should be done better
    CHUNK_SIZE = 1048576
    data_checked = False
    is_compressed = False
    is_binary = False
    try:
        codecs.lookup(target_encoding)
    except Exception:
        target_encoding = util.DEFAULT_ENCODING  # utf-8
    if not source_encoding:
        source_encoding = util.DEFAULT_ENCODING  # sys.getdefaultencoding() would mimic old behavior (defaults to ascii)
    while True:
        chunk = stream.read(CHUNK_SIZE)
        if not chunk:
            break
        if not data_checked:
            # See if we're uploading a compressed file
            if zipfile.is_zipfile(filename):
                is_compressed = True
            else:
                try:
                    if text_type(chunk[:2]) == text_type(util.gzip_magic):
                        is_compressed = True
                except Exception:
                    pass
            if not is_compressed:
                is_binary = util.is_binary(chunk)
            data_checked = True
        if not is_compressed and not is_binary:
            if not isinstance(chunk, text_type):
                chunk = chunk.decode(source_encoding, source_error)
            os.write(fd, chunk.encode(target_encoding, target_error))
        else:
            # Compressed files must be encoded after they are uncompressed in the upload utility,
            # while binary files should not be encoded at all.
            os.write(fd, chunk)
    os.close(fd)
    return filename


def stream_to_file(stream, suffix='', prefix='', dir=None, text=False, **kwd):
    """Writes a stream to a temporary file, returns the temporary file's name"""
    fd, temp_name = tempfile.mkstemp(suffix=suffix, prefix=prefix, dir=dir, text=text)
    return stream_to_open_named_file(stream, fd, temp_name, **kwd)


def convert_newlines(fname, in_place=True, tmp_dir=None, tmp_prefix="gxupload"):
    """
    Converts in place a file from universal line endings
    to Posix line endings.

    >>> fname = get_test_fname('temp.txt')
    >>> open(fname, 'wt').write("1 2\\r3 4")
    >>> convert_newlines(fname, tmp_prefix="gxtest", tmp_dir=tempfile.gettempdir())
    (2, None)
    >>> open(fname).read()
    '1 2\\n3 4\\n'
    """
    fd, temp_name = tempfile.mkstemp(prefix=tmp_prefix, dir=tmp_dir)
    with os.fdopen(fd, "wt") as fp:
        i = None
        for i, line in enumerate(open(fname, "U")):
            fp.write("%s\n" % line.rstrip("\r\n"))
    if i is None:
        i = 0
    else:
        i += 1
    if in_place:
        shutil.move(temp_name, fname)
        # Return number of lines in file.
        return (i, None)
    else:
        return (i, temp_name)


def sep2tabs(fname, in_place=True, patt="\\s+", tmp_dir=None, tmp_prefix="gxupload"):
    """
    Transforms in place a 'sep' separated file to a tab separated one

    >>> fname = get_test_fname('temp.txt')
    >>> open(fname, 'wt').write("1 2\\n3 4\\n")
    >>> sep2tabs(fname)
    (2, None)
    >>> open(fname).read()
    '1\\t2\\n3\\t4\\n'
    """
    regexp = re.compile(patt)
    fd, temp_name = tempfile.mkstemp(prefix=tmp_prefix, dir=tmp_dir)
    with os.fdopen(fd, "wt") as fp:
        i = None
        for i, line in enumerate(open(fname)):
            if line.endswith("\r"):
                line = line.rstrip('\r')
                elems = regexp.split(line)
                fp.write("%s\r" % '\t'.join(elems))
            else:
                line = line.rstrip('\n')
                elems = regexp.split(line)
                fp.write("%s\n" % '\t'.join(elems))
    if i is None:
        i = 0
    else:
        i += 1
    if in_place:
        shutil.move(temp_name, fname)
        # Return number of lines in file.
        return (i, None)
    else:
        return (i, temp_name)


def convert_newlines_sep2tabs(fname, in_place=True, patt="\\s+", tmp_dir=None, tmp_prefix="gxupload"):
    """
    Combines above methods: convert_newlines() and sep2tabs()
    so that files do not need to be read twice

    >>> fname = get_test_fname('temp.txt')
    >>> open(fname, 'wt').write("1 2\\r3 4")
    >>> convert_newlines_sep2tabs(fname, tmp_prefix="gxtest", tmp_dir=tempfile.gettempdir())
    (2, None)
    >>> open(fname).read()
    '1\\t2\\n3\\t4\\n'
    """
    regexp = re.compile(patt)
    fd, temp_name = tempfile.mkstemp(prefix=tmp_prefix, dir=tmp_dir)
    with os.fdopen(fd, "wt") as fp:
        for i, line in enumerate(open(fname, "U")):
            line = line.rstrip('\r\n')
            elems = regexp.split(line)
            fp.write("%s\n" % '\t'.join(elems))
    if in_place:
        shutil.move(temp_name, fname)
        # Return number of lines in file.
        return (i + 1, None)
    else:
        return (i + 1, temp_name)


def iter_headers(fname_or_file_prefix, sep, count=60, comment_designator=None):
    if isinstance(fname_or_file_prefix, FilePrefix):
        idx = 0
        for line in fname_or_file_prefix.line_iterator():
            line = line.rstrip('\n\r')
            if comment_designator is not None and comment_designator != '' and line.startswith(comment_designator):
                continue
            yield line.split(sep)
            idx += 1
            if idx == count:
                break
    else:
        with compression_utils.get_fileobj(fname_or_file_prefix) as in_file:
            idx = 0
            for line in in_file:
                line = line.rstrip('\n\r')
                if comment_designator is not None and comment_designator != '' and line.startswith(comment_designator):
                    continue
                yield line.split(sep)
                idx += 1
                if idx == count:
                    break


def get_headers(fname_or_file_prefix, sep, count=60, comment_designator=None):
    """
    Returns a list with the first 'count' lines split by 'sep', ignoring lines
    starting with 'comment_designator'

    >>> fname = get_test_fname('complete.bed')
    >>> get_headers(fname,'\\t') == [['chr7', '127475281', '127491632', 'NM_000230', '0', '+', '127486022', '127488767', '0', '3', '29,172,3225,', '0,10713,13126,'], ['chr7', '127486011', '127488900', 'D49487', '0', '+', '127486022', '127488767', '0', '2', '155,490,', '0,2399']]
    True
    >>> fname = get_test_fname('test.gff')
    >>> get_headers(fname, '\\t', count=5, comment_designator='#') == [[''], ['chr7', 'bed2gff', 'AR', '26731313', '26731437', '.', '+', '.', 'score'], ['chr7', 'bed2gff', 'AR', '26731491', '26731536', '.', '+', '.', 'score'], ['chr7', 'bed2gff', 'AR', '26731541', '26731649', '.', '+', '.', 'score'], ['chr7', 'bed2gff', 'AR', '26731659', '26731841', '.', '+', '.', 'score']]
    True
    """
    return list(iter_headers(fname_or_file_prefix=fname_or_file_prefix, sep=sep, count=count, comment_designator=comment_designator))


def is_column_based(fname_or_file_prefix, sep='\t', skip=0):
    """
    Checks whether the file is column based with respect to a separator
    (defaults to tab separator).

    >>> fname = get_test_fname('test.gff')
    >>> is_column_based(fname)
    True
    >>> fname = get_test_fname('test_tab.bed')
    >>> is_column_based(fname)
    True
    >>> is_column_based(fname, sep=' ')
    False
    >>> fname = get_test_fname('test_space.txt')
    >>> is_column_based(fname)
    False
    >>> is_column_based(fname, sep=' ')
    True
    >>> fname = get_test_fname('test_ensembl.tab')
    >>> is_column_based(fname)
    True
    >>> fname = get_test_fname('test_tab1.tabular')
    >>> is_column_based(fname, sep=' ', skip=0)
    False
    >>> fname = get_test_fname('test_tab1.tabular')
    >>> is_column_based(fname)
    True
    """
    if getattr(fname_or_file_prefix, "binary", None) is True:
        return False

    try:
        headers = get_headers(fname_or_file_prefix, sep)
    except UnicodeDecodeError:
        return False
    count = 0
    if not headers:
        return False
    for hdr in headers[skip:]:
        if hdr and hdr[0] and not hdr[0].startswith('#'):
            if len(hdr) > 1:
                count = len(hdr)
            break
    if count < 2:
        return False
    for hdr in headers[skip:]:
        if hdr and hdr[0] and not hdr[0].startswith('#'):
            if len(hdr) != count:
                return False
    return True


def guess_ext(fname, sniff_order, is_binary=False):
    """
    Returns an extension that can be used in the datatype factory to
    generate a data for the 'fname' file

    >>> from galaxy.datatypes.registry import example_datatype_registry_for_sample
    >>> datatypes_registry = example_datatype_registry_for_sample()
    >>> sniff_order = datatypes_registry.sniff_order
    >>> fname = get_test_fname('megablast_xml_parser_test1.blastxml')
    >>> guess_ext(fname, sniff_order)
    'blastxml'
    >>> fname = get_test_fname('interval.interval')
    >>> guess_ext(fname, sniff_order)
    'interval'
    >>> fname = get_test_fname('interval1.bed')
    >>> guess_ext(fname, sniff_order)
    'bed'
    >>> fname = get_test_fname('test_tab.bed')
    >>> guess_ext(fname, sniff_order)
    'bed'
    >>> fname = get_test_fname('sequence.maf')
    >>> guess_ext(fname, sniff_order)
    'maf'
    >>> fname = get_test_fname('sequence.fasta')
    >>> guess_ext(fname, sniff_order)
    'fasta'
    >>> fname = get_test_fname('1.genbank')
    >>> guess_ext(fname, sniff_order)
    'genbank'
    >>> fname = get_test_fname('1.genbank.gz')
    >>> guess_ext(fname, sniff_order)
    'genbank.gz'
    >>> fname = get_test_fname('file.html')
    >>> guess_ext(fname, sniff_order)
    'html'
    >>> fname = get_test_fname('test.gtf')
    >>> guess_ext(fname, sniff_order)
    'gtf'
    >>> fname = get_test_fname('test.gff')
    >>> guess_ext(fname, sniff_order)
    'gff'
    >>> fname = get_test_fname('gff_version_3.gff')
    >>> guess_ext(fname, sniff_order)
    'gff3'
    >>> fname = get_test_fname('2.txt')
    >>> guess_ext(fname, sniff_order)  # 2.txt
    'txt'
    >>> fname = get_test_fname('2.tabular')
    >>> guess_ext(fname, sniff_order)
    'tabular'
    >>> fname = get_test_fname('3.txt')
    >>> guess_ext(fname, sniff_order)  # 3.txt
    'txt'
    >>> fname = get_test_fname('test_tab1.tabular')
    >>> guess_ext(fname, sniff_order)
    'tabular'
    >>> fname = get_test_fname('alignment.lav')
    >>> guess_ext(fname, sniff_order)
    'lav'
    >>> fname = get_test_fname('1.sff')
    >>> guess_ext(fname, sniff_order)
    'sff'
    >>> fname = get_test_fname('1.bam')
    >>> guess_ext(fname, sniff_order)
    'bam'
    >>> fname = get_test_fname('3unsorted.bam')
    >>> guess_ext(fname, sniff_order)
    'unsorted.bam'
    >>> fname = get_test_fname('test.idpDB')
    >>> guess_ext(fname, sniff_order)
    'idpdb'
    >>> fname = get_test_fname('test.mz5')
    >>> guess_ext(fname, sniff_order)
    'h5'
    >>> fname = get_test_fname('issue1818.tabular')
    >>> guess_ext(fname, sniff_order)
    'tabular'
    >>> fname = get_test_fname('drugbank_drugs.cml')
    >>> guess_ext(fname, sniff_order)
    'cml'
    >>> fname = get_test_fname('q.fps')
    >>> guess_ext(fname, sniff_order)
    'fps'
    >>> fname = get_test_fname('drugbank_drugs.inchi')
    >>> guess_ext(fname, sniff_order)
    'inchi'
    >>> fname = get_test_fname('drugbank_drugs.mol2')
    >>> guess_ext(fname, sniff_order)
    'mol2'
    >>> fname = get_test_fname('drugbank_drugs.sdf')
    >>> guess_ext(fname, sniff_order)
    'sdf'
    >>> fname = get_test_fname('5e5z.pdb')
    >>> guess_ext(fname, sniff_order)
    'pdb'
    >>> fname = get_test_fname('mothur_datatypetest_true.mothur.otu')
    >>> guess_ext(fname, sniff_order)
    'mothur.otu'
    >>> fname = get_test_fname('mothur_datatypetest_true.mothur.lower.dist')
    >>> guess_ext(fname, sniff_order)
    'mothur.lower.dist'
    >>> fname = get_test_fname('mothur_datatypetest_true.mothur.square.dist')
    >>> guess_ext(fname, sniff_order)
    'mothur.square.dist'
    >>> fname = get_test_fname('mothur_datatypetest_true.mothur.pair.dist')
    >>> guess_ext(fname, sniff_order)
    'mothur.pair.dist'
    >>> fname = get_test_fname('mothur_datatypetest_true.mothur.freq')
    >>> guess_ext(fname, sniff_order)
    'mothur.freq'
    >>> fname = get_test_fname('mothur_datatypetest_true.mothur.quan')
    >>> guess_ext(fname, sniff_order)
    'mothur.quan'
    >>> fname = get_test_fname('mothur_datatypetest_true.mothur.ref.taxonomy')
    >>> guess_ext(fname, sniff_order)
    'mothur.ref.taxonomy'
    >>> fname = get_test_fname('mothur_datatypetest_true.mothur.axes')
    >>> guess_ext(fname, sniff_order)
    'mothur.axes'
    >>> guess_ext(get_test_fname('infernal_model.cm'), sniff_order)
    'cm'
    >>> fname = get_test_fname('1.gg')
    >>> guess_ext(fname, sniff_order)
    'gg'
    >>> fname = get_test_fname('diamond_db.dmnd')
    >>> guess_ext(fname, sniff_order)
    'dmnd'
    >>> fname = get_test_fname('1.xls')
    >>> guess_ext(fname, sniff_order)
    'excel.xls'
    >>> fname = get_test_fname('biom2_sparse_otu_table_hdf5.biom')
    >>> guess_ext(fname, sniff_order)
    'biom2'
    >>> fname = get_test_fname('454Score.pdf')
    >>> guess_ext(fname, sniff_order)
    'pdf'
    >>> fname = get_test_fname('1.obo')
    >>> guess_ext(fname, sniff_order)
    'obo'
    >>> fname = get_test_fname('1.arff')
    >>> guess_ext(fname, sniff_order)
    'arff'
    >>> fname = get_test_fname('1.afg')
    >>> guess_ext(fname, sniff_order)
    'afg'
    >>> fname = get_test_fname('1.owl')
    >>> guess_ext(fname, sniff_order)
    'owl'
    >>> fname = get_test_fname('Acanium.hmm')
    >>> guess_ext(fname, sniff_order)
    'snaphmm'
    >>> fname = get_test_fname('wiggle.wig')
    >>> guess_ext(fname, sniff_order)
    'wig'
    >>> fname = get_test_fname('example.iqtree')
    >>> guess_ext(fname, sniff_order)
    'iqtree'
    >>> fname = get_test_fname('1.stockholm')
    >>> guess_ext(fname, sniff_order)
    'stockholm'
    >>> fname = get_test_fname('1.xmfa')
    >>> guess_ext(fname, sniff_order)
    'xmfa'
    >>> fname = get_test_fname('test.phylip')
    >>> guess_ext(fname, sniff_order)
    'phylip'
    >>> fname = get_test_fname('1.smat')
    >>> guess_ext(fname, sniff_order)
    'smat'
    >>> fname = get_test_fname('1.ttl')
    >>> guess_ext(fname, sniff_order)
    'ttl'
    >>> fname = get_test_fname('1.hdt')
    >>> guess_ext(fname, sniff_order)
    'hdt'
    >>> fname = get_test_fname('1.phyloxml')
    >>> guess_ext(fname, sniff_order)
    'phyloxml'
    >>> fname = get_test_fname('1.fastqsanger.gz')
    >>> guess_ext(fname, sniff_order)  # See test_datatype_registry for more compressed type tests.
    'fastqsanger.gz'
    """
    file_prefix = FilePrefix(fname)
    file_ext = run_sniffers_raw(file_prefix, sniff_order, is_binary)

    # Ugly hack for tsv vs tabular sniffing, we want to prefer tabular
    # to tsv but it doesn't have a sniffer - is TSV was sniffed just check
    # if it is an okay tabular and use that instead.
    if file_ext == 'tsv':
        if is_column_based(file_prefix, '\t', 1):
            file_ext = 'tabular'
    if file_ext is not None:
        return file_ext

    # skip header check if data is already known to be binary
    if is_binary:
        return file_ext or 'binary'
    try:
        get_headers(file_prefix, None)
    except UnicodeDecodeError:
        return 'data'  # default data type file extension
    if is_column_based(file_prefix, '\t', 1):
        return 'tabular'  # default tabular data type file extension
    return 'txt'  # default text data type file extension


def run_sniffers_raw(filename_or_file_prefix, sniff_order, is_binary=False):
    """Run through sniffers specified by sniff_order, return None of None match.
    """
    if isinstance(filename_or_file_prefix, FilePrefix):
        fname = filename_or_file_prefix.filename
        file_prefix = filename_or_file_prefix
    else:
        fname = filename_or_file_prefix
        file_prefix = FilePrefix(filename_or_file_prefix)

    file_ext = None
    for datatype in sniff_order:
        """
        Some classes may not have a sniff function, which is ok.  In fact,
        Binary, Data, Tabular and Text are examples of classes that should never
        have a sniff function. Since these classes are default classes, they contain
        few rules to filter out data of other formats, so they should be called
        from this function after all other datatypes in sniff_order have not been
        successfully discovered.
        """
        try:
            if hasattr(datatype, "sniff_prefix"):
                datatype_compressed = getattr(datatype, "compressed", False)
                if datatype_compressed and not file_prefix.compressed_format:
                    continue
                if not datatype_compressed and file_prefix.compressed_format:
                    continue
                if file_prefix.compressed_format and getattr(datatype, "compressed_format"):
                    # In this case go a step further and compare the compressed format detected
                    # to the expected.
                    if file_prefix.compressed_format != datatype.compressed_format:
                        continue
                if datatype.sniff_prefix(file_prefix):
                    file_ext = datatype.file_ext
                    break
            elif is_binary and not datatype.is_binary:
                continue
            elif datatype.sniff(fname):
                file_ext = datatype.file_ext
                break
        except Exception:
            pass

    return file_ext


def zip_single_fileobj(path):
    z = zipfile.ZipFile(path)
    for name in z.namelist():
        if not name.endswith('/'):
            return z.open(name)


class FilePrefix(object):

    def __init__(self, filename):
        binary = False
        compressed_format = None
        contents_header = None  # First MAX_BYTES of the file.
        truncated = False
        # A future direction to optimize sniffing even more for sniffers at the top of the list
        # is to lazy load contents_header based on what interface is requested. For instance instead
        # of returning a StringIO directly in string_io() return an object that reads the contents and
        # populates contents_header while providing a StringIO-like interface until the file is read
        # but then would fallback to native string_io()
        try:
            compressed_format, f = compression_utils.get_fileobj_raw(filename)
            try:
                contents_header = f.read(SNIFF_PREFIX_BYTES)
                truncated = len(contents_header) == SNIFF_PREFIX_BYTES
            finally:
                f.close()
        except UnicodeDecodeError:
            binary = True

        self.truncated = truncated
        self.filename = filename
        self.binary = binary
        self.compressed_format = compressed_format
        self.contents_header = contents_header
        self._file_size = None

    @property
    def file_size(self):
        if self._file_size is None:
            self._file_size = os.path.getsize(self.filename)
        return self._file_size

    def string_io(self):
        if self.binary:
            raise Exception("Attempting to create a StringIO object for binary data.")
        rval = StringIO(self.contents_header)
        return rval

    def startswith(self, prefix):
        return self.string_io().read(len(prefix)) == prefix

    def line_iterator(self):
        s = self.string_io()
        for line in s:
            if line.endswith("\n") or line.endswith("\r"):
                yield line
            elif s.pos == s.len and not self.truncated:
                # At the end, return the last line if it wasn't truncated when reading it in.
                yield line

    # Convenience wrappers around contents_header, shielding contents_header means we can
    # potentially do a better job lazy loading this data later on.
    def search(self, pattern):
        return pattern.search(self.contents_header)

    def search_str(self, query_str):
        return query_str in self.contents_header


def build_sniff_from_prefix(klass):
    # Build and attach a sniff function to this class (klass) from the sniff_prefix function
    # expected to be defined for the class.
    def auto_sniff(self, filename):
        file_prefix = FilePrefix(filename)
        datatype_compressed = getattr(self, "compressed", False)
        if file_prefix.compressed_format and not datatype_compressed:
            return False
        if datatype_compressed:
            if not file_prefix.compressed_format:
                # This not a compressed file we are looking but the type expects it to be
                # must return False.
                return False

        if hasattr(self, "compressed_format"):
            if self.compressed_format != file_prefix.compressed_format:
                return False
        return self.sniff_prefix(file_prefix)

    klass.sniff = auto_sniff
    return klass


def disable_parent_class_sniffing(klass):
    klass.sniff = lambda self, filename: False
    klass.sniff_prefix = lambda self, file_prefix: False
    return klass


def handle_compressed_file(
        filename,
        datatypes_registry,
        ext='auto',
        tmp_prefix='sniff_uncompress_',
        tmp_dir=None,
        in_place=False,
        check_content=True,
        auto_decompress=True,
):
    """
    Check uploaded files for compression, check compressed file contents, and uncompress if necessary.

    Supports GZip, BZip2, and the first file in a Zip file.

    For performance reasons, the temporary file used for uncompression is located in the same directory as the
    input/output file. This behavior can be changed with the `tmp_dir` param.

    ``ext`` as returned will only be changed from the ``ext`` input param if the param was an autodetect type (``auto``)
    and the file was sniffed as a keep-compressed datatype.

    ``is_valid`` as returned will only be set if the file is compressed and contains invalid contents (or the first file
    in the case of a zip file), this is so lengthy decompression can be bypassed if there is invalid content in the
    first 32KB. Otherwise the caller should be checking content.
    """
    CHUNK_SIZE = 2 ** 20  # 1Mb
    is_compressed = False
    compressed_type = None
    keep_compressed = False
    is_valid = False
    uncompressed = filename
    tmp_dir = tmp_dir or os.path.dirname(filename)
    for compressed_type, check_compressed_function in COMPRESSION_CHECK_FUNCTIONS:
        is_compressed, is_valid = check_compressed_function(filename, check_content=check_content)
        if is_compressed:
            break  # found compression type
    if is_compressed and is_valid:
        if ext in AUTO_DETECT_EXTENSIONS:
            # attempt to sniff for a keep-compressed datatype (observing the sniff order)
            sniff_datatypes = filter(lambda d: getattr(d, 'compressed', False), datatypes_registry.sniff_order)
            sniffed_ext = run_sniffers_raw(filename, sniff_datatypes)
            if sniffed_ext:
                ext = sniffed_ext
                keep_compressed = True
        else:
            datatype = datatypes_registry.get_datatype_by_extension(ext)
            keep_compressed = getattr(datatype, 'compressed', False)
    # don't waste time decompressing if we sniff invalid contents
    if is_compressed and is_valid and auto_decompress and not keep_compressed:
        fd, uncompressed = tempfile.mkstemp(prefix=tmp_prefix, dir=tmp_dir)
        compressed_file = DECOMPRESSION_FUNCTIONS[compressed_type](filename)
        # TODO: it'd be ideal to convert to posix newlines and space-to-tab here as well
        while True:
            try:
                chunk = compressed_file.read(CHUNK_SIZE)
            except IOError as e:
                os.close(fd)
                os.remove(uncompressed)
                compressed_file.close()
                raise IOError('Problem uncompressing %s data, please try retrieving the data uncompressed: %s' % (compressed_type, e))
            if not chunk:
                break
            os.write(fd, chunk)
        os.close(fd)
        compressed_file.close()
        if in_place:
            # Replace the compressed file with the uncompressed file
            shutil.move(uncompressed, filename)
            uncompressed = filename
    elif not is_compressed or not check_content:
        is_valid = True
    return is_valid, ext, uncompressed, compressed_type


def handle_uploaded_dataset_file(*args, **kwds):
    """Legacy wrapper about handle_uploaded_dataset_file_internal for tools using it."""
    return handle_uploaded_dataset_file_internal(*args, **kwds)[0]


def handle_uploaded_dataset_file_internal(
        filename,
        datatypes_registry,
        ext='auto',
        tmp_prefix='sniff_upload_',
        tmp_dir=None,
        in_place=False,
        check_content=True,
        is_binary=None,
        auto_decompress=True,
        uploaded_file_ext=None,
        convert_to_posix_lines=None,
        convert_spaces_to_tabs=None,
):
    is_valid, ext, converted_path, compressed_type = handle_compressed_file(
        filename,
        datatypes_registry,
        ext=ext,
        tmp_prefix=tmp_prefix,
        tmp_dir=tmp_dir,
        in_place=in_place,
        check_content=check_content,
        auto_decompress=auto_decompress,
    )
    try:
        if not is_valid:
            if is_tar(converted_path):
                raise InappropriateDatasetContentError('TAR file uploads are not supported')
            raise InappropriateDatasetContentError('The uploaded compressed file contains invalid content')

        # This needs to be checked again after decompression
        is_binary = check_binary(converted_path)

        if not is_binary and (convert_to_posix_lines or convert_spaces_to_tabs):
            # Convert universal line endings to Posix line endings, spaces to tabs (if desired)
            if convert_spaces_to_tabs:
                convert_fxn = convert_newlines_sep2tabs
            else:
                convert_fxn = convert_newlines
            line_count, _converted_path = convert_fxn(converted_path, in_place=in_place, tmp_dir=tmp_dir, tmp_prefix=tmp_prefix)
            if not in_place:
                if converted_path and filename != converted_path:
                    os.unlink(converted_path)
                converted_path = _converted_path

        if ext in AUTO_DETECT_EXTENSIONS:
            ext = guess_ext(converted_path, sniff_order=datatypes_registry.sniff_order, is_binary=is_binary)

        if not is_binary and check_content and check_html(converted_path):
            raise InappropriateDatasetContentError('The uploaded file contains invalid HTML content')
    except Exception:
        if filename != converted_path:
            os.unlink(converted_path)
        raise
    return ext, converted_path, compressed_type


AUTO_DETECT_EXTENSIONS = ['auto']  # should 'data' also cause auto detect?
DECOMPRESSION_FUNCTIONS = dict(gz=gzip.GzipFile, bz2=bz2.BZ2File, zip=zip_single_fileobj)
COMPRESSION_CHECK_FUNCTIONS = [('gz', check_gzip), ('bz2', check_bz2), ('zip', check_zip)]


class InappropriateDatasetContentError(Exception):
    pass


if __name__ == '__main__':
    import doctest
    doctest.testmod(sys.modules[__name__])
