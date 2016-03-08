var renderer3D = null;
var scene3D = null;
var camera3D = null;
var scatterPlot3D = null;

var displayToolbar3D = function(toolbarDiv3D,populationDiv3D,scatterData3D) {
    scatterData3D['columnHeadings'].map(function(value,index) {
        $('#xAxisMarker3D')
            .append($("<option></option>")
            .attr("value",index)
            .text(value));

        $('#yAxisMarker3D')
            .append($("<option></option>")
            .attr("value",index)
            .text(value));

        $('#zAxisMarker3D')
            .append($("<option></option>")
            .attr("value",index)
            .text(value));
    });

    $('#xAxisMarker3D').select2("val",0);
    $('#yAxisMarker3D').select2("val",1);
    $('#zAxisMarker3D').select2("val",2);

    scatterData3D['populations'].map(function(value,index) {
        $('#populationTable3D tr')
            .last()
            .after('<tr><td align="center"><input type="checkbox" checked class="pop3D" value=' + value + '/></td><td>' + value + '<td><span style="background-color:' + color_palette[value] + '">&nbsp;&nbsp;&nbsp</span></td></td><td>' + scatterData3D['percent'][value - 1] + '<td></tr>');
    });

    return;
};

var processScatterData3D = function(scatterData3D) {
    var min = d3.min(scatterData3D['data'], function(array) {
      return d3.min(array);
    });
    var max = d3.max(scatterData3D['data'], function(array) {
      return d3.max(array);
    });
    scatterData3D['min'] = 0;
    scatterData3D['max'] = max;

    var col1 = scatterData3D['data'].map(function(value,index) {
               return value[scatterData3D['m1']];});
    var col2 = scatterData3D['data'].map(function(value,index) {
               return value[scatterData3D['m2']];});
    var col3 = scatterData3D['data'].map(function(value,index) {
               return value[scatterData3D['m3']];});
    var pop = scatterData3D['data'].map(function(value,index) {
               return value[scatterData3D['popCol']];});

    var xData = [];
    var yData = [];
    var zData = [];
    var popData = [];
    for (var i = 0; i < col1.length; i++) {
        if (scatterData3D['populations'].indexOf(pop[i]) >= 0) {
            xData.push(col1[i]);
            yData.push(col2[i]);
            zData.push(col3[i]);
            popData.push(pop[i]);
        }
    }
    scatterData3D['xData'] = xData;
    scatterData3D['yData'] = yData;
    scatterData3D['zData'] = zData;
    scatterData3D['popData'] = popData;
    return scatterData3D;
};


var displayScatterPlot3D = function() {
    $('#scatterPlotDiv3D').empty();

    renderer3D = null;
    scene3D = null;
    camera3D = null;
    scatterPlot3D = null;

    setupRenderer("#scatterPlotDiv3D");
    setupCamera();
    setupScene();
    function v(x,y,z) {
        return new THREE.Vector3(x,y,z);
    }

    var xExtent = d3.extent(scatterData3D['xData'], function (d) {return d }),
        yExtent = d3.extent(scatterData3D['yData'], function (d) {return d }),
        zExtent = d3.extent(scatterData3D['zData'], function (d) {return d });

    var m = d3.max([xExtent[1],yExtent[1],zExtent[1]])
    var xExtent = [0,m];
    var yExtent = [0,m];
    var zExtent = [0,m];

    var vpts = {
        xMax: xExtent[1],
        xCen: (xExtent[1] + xExtent[0]) / 2,
        xMin: xExtent[0],
        yMax: yExtent[1],
        yCen: (yExtent[1] + yExtent[0]) / 2,
        yMin: yExtent[0],
        zMax: zExtent[1],
        zCen: (zExtent[1] + zExtent[0]) / 2,
        zMin: zExtent[0]
    }

    var colour = d3.scale.category20c();
    var xScale = d3.scale.linear()
                  .domain(xExtent)
                  .range([0,100]);
    var yScale = d3.scale.linear()
                  .domain(yExtent)
                  .range([0,100]);
    var zScale = d3.scale.linear()
                  .domain(zExtent)
                  .range([0,100]);

    var lineGeoX = new THREE.Geometry();
    var lineGeoY = new THREE.Geometry();
    var lineGeoZ = new THREE.Geometry();

    lineGeoY.vertices.push(
        v(xScale(vpts.xMin), yScale(vpts.yMin), zScale(vpts.zMin)),
        v(xScale(vpts.xMin), yScale(vpts.yMax), zScale(vpts.zMin))
    )
    lineGeoX.vertices.push(
        v(xScale(vpts.xMin), yScale(vpts.yMin), zScale(vpts.zMin)),
        v(xScale(vpts.xMax), yScale(vpts.yMin), zScale(vpts.zMin))
    )
    lineGeoZ.vertices.push(
        v(xScale(vpts.xMin), yScale(vpts.yMin), zScale(vpts.zMin)),
        v(xScale(vpts.xMin), yScale(vpts.yMin), zScale(vpts.zMax))
    )

    var lineMat = new THREE.LineBasicMaterial({
        color: 0x000000
    });
    var line = new THREE.Line(lineGeoX, lineMat);
    line.type = THREE.Lines;
    scatterPlot3D.add(line);
    var line = new THREE.Line(lineGeoY, lineMat);
    line.type = THREE.Lines;
    scatterPlot3D.add(line);
    var line = new THREE.Line(lineGeoZ, lineMat);
    line.type = THREE.Lines;
    scatterPlot3D.add(line);

    var pointCount = scatterData3D['xData'].length;
    var geometry = new THREE.BufferGeometry();
    var positions = new Float32Array( pointCount * 3 );
    var colors = new Float32Array( pointCount * 3);
    var col = new THREE.Color("steelblue");
    var scale = 2;
    for ( var i = 0; i < pointCount; i++ ) {
        var start = i * 3;
        var x = xScale(scatterData3D['xData'][i]);
        var y = yScale(scatterData3D['yData'][i]);
        var z = zScale(scatterData3D['zData'][i]);
        positions[start] = x;
        positions[start + 1] = y;
        positions[start + 2] = z;
    }


    for ( var i = 0; i < pointCount; i++) {
        j = i * 3;
        //colors[j] = col.r;
        //colors[j+1] = col.g;
        //colors[j+2] = col.b;
        var col = new THREE.Color(color_palette[scatterData3D['popData'][i]]);
        colors[j] = col.r;
        colors[j+1] = col.g;
        colors[j+2] = col.b;
    }
    geometry.addAttribute( 'position', new THREE.BufferAttribute( positions, 3 ) );
    geometry.addAttribute( 'color', new THREE.BufferAttribute( colors, 3 ) );
    geometry.computeBoundingSphere();
    var pcmaterial = new THREE.PointsMaterial( { size: scale, vertexColors: THREE.VertexColors } );
    var particleSystem = new THREE.Points( geometry, pcmaterial );
    scatterPlot3D.add( particleSystem );

    renderer3D.render(scene3D,camera3D);
    var paused = false;
    var last = new Date().getTime();
    var down = false;
    var sx = 0,
        sy = 0;

    $('#scatterPlotDiv3D').on('mousedown',function(ev) {
        down = true;
        sx = ev.clientX;
        sy = ev.clientY;
    });
    $('#scatterPlotDiv3D').on('mouseup',function() {
        down = false;
    });
    $('#scatterPlotDiv3D').on('mousemove',function(ev) {
        if (down) {
            var dx = ev.clientX - sx;
            var dy = ev.clientY - sy;
            scatterPlot3D.rotation.y += dx * 0.01;
            camera3D.position.y += dy;
            sx += dx;
            sy += dy;
        }
    });
    var animating = false;
    $('#scatterPlotDiv3D').on('dblclick',function() {
        animating = !animating;
    });

   function animate(t) {
        if (!paused) {
            last = t;
            if (animating) {
                var v = pointGeo.vertices;
                for (var i = 0; i < v.length; i++) {
                    var u = v[i];
                    u.angle += u.speed * 0.01;
                    u.x = Math.cos(u.angle) * u.radius;
                    u.z = Math.sin(u.angle) * u.radius;
                }
                pointGeo.__dirtyVertices = true;
            }
            renderer3D.clear();
            camera3D.lookAt(scene3D.position);
            renderer3D.render(scene3D, camera3D);
        }
        window.requestAnimationFrame(animate, renderer3D.domElement);
    };
    animate(new Date().getTime());
    onmessage = function(ev) {
        paused = (ev.data == 'pause');
    };
}

function setupRenderer(element) {
    //var h = $(window).height() - 200;
    //$(element).empty();
    //$(element).height(h);
    var iframe = window.parent.document.getElementById('galaxy_main')
    var iframeHeight = iframe.clientHeight;
    var iframeWidth = iframe.clientWidth;
    console.log($(window).width(),$(window).height());
    console.log(iframeWidth,iframeHeight);
    var h = iframeHeight - 200;
    $(element).empty();
    $(element).height(iframeHeight - 200);

    canvasWidth = $(element).width();
    canvasHeight = $(element).height();

    var test_canvas = document.createElement('canvas');
    var gl = null;
    try {
        GL = ( test_canvas.getContext("webgl") ||
               test_canvas.getContext("experimental-webgl")
             );
    } catch(e) {
    }
    if (GL) {
        renderer3D = new THREE.WebGLRenderer( {antialias: true} );
    } else {
        renderer3D = new THREE.CanvasRenderer();
    }
    test_canvas = undefined;

    renderer3D.setSize( canvasWidth, canvasHeight );
    renderer3D.setClearColor(0xEEEEEE, 1.0);
    $(element).append( renderer3D.domElement );
}

function setupScene() {
    scene3D = new THREE.Scene();
    scatterPlot3D = new THREE.Object3D();
    scene3D.add(scatterPlot3D);
}

function setupCamera() {
    camera3D = new THREE.PerspectiveCamera(50, canvasWidth/canvasHeight, 1, 10000);
    camera3D.position.z = 250;
}
