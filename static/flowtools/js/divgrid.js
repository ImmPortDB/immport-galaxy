// http://bl.ocks.org/3687826
d3.divgrid = function(config) {
  var columns = [];

  var dg = function(selection) {
    if (columns.length == 0) columns = d3.keys(selection.data()[0][0]);

    // header
    selection.selectAll(".gridHeader")
        .data([true])
      .enter().append("div")
        .attr("class", "gridHeader")

    var header = selection.select(".gridHeader")
      .selectAll(".gridCell")
      .data(columns);

    header.enter().append("div")
      .attr("class", function(d,i) { return "col-" + i; })
      .classed("gridCell", true)

    selection.selectAll(".gridHeader .gridCell")
      .text(function(d) { return d; });

    header.exit().remove();

    // rows
    var rows = selection.selectAll(".gridRow")
        .data(function(d) { return d; })

    rows.enter().append("div")
        .attr("class", "gridRow")

    rows.exit().remove();

    var cells = selection.selectAll(".gridRow").selectAll(".gridCell")
        .data(function(d) { return columns.map(function(col){return d[col];}) })

    // cells
    cells.enter().append("div")
      .attr("class", function(d,i) { return "col-" + i; })
      .classed("gridCell", true)

    cells.exit().remove();

    selection.selectAll(".gridCell")
      .text(function(d) { return d; });

    return dg;
  };

  dg.columns = function(_) {
    if (!arguments.length) return columns;
    columns = _;
    return this;
  };

  return dg;
};
