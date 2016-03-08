var color_palette = [
    '#000000', // Black 0
    '#FF0000', // Red 1
    '#FFFF00', // Yellow 2
    '#008000', // Dark Green 3
    '#0000FF', // Blue 4
    '#FFA500', // Orange 5
    '#8A2BE2', // BlueViolet 6
    '#808000', // Olive 7
    '#00FFFF', // Cyan 8
    '#FF00FF', // Magenta 9
    '#00FF00', // Green 10
    '#000080', // Navy Blue 11
    '#F08080', // Light Coral 12
    '#800080', // Purple 13
    '#F0E68C', // Khaki 14
    '#8FBC8F', // Dark Sea Green 15
    '#2F4F4F', // Dark Slate Grey 16
    '#008080', // Teal 17
    '#9932CC', // Dark Orchid 18
    '#FF7F50', // Coral 19
    '#FFD700', // Gold 20
    '#008B8B', // Cyan 4 21
    '#800000', // Maroon 22
    '#5F9EA0', // Cadet Blue 23
    '#FFC0CB', // Pink 24
    '#545454', // Grey 25
    '#7FFFD4', // Aquamarine 26
    '#ADD8E6', // Light Blue 27
    '#DB7093', // Medium Violet Red 28
    '#CD853F', // Tan 3 29
    '#4169E1', // Royal Blue 30
    '#708090', // Slate Grey 31
    '#4682B4', // Steel Blue 32
    '#D8BFD8', // Thistle 33
    '#F5DEB3', // Wheat 34
    '#9ACD32', // Yellow Green 35
    '#BDB76B', // Dark Khaki 36
    '#8B008B', // Magenta 4 37
    '#556B2F', // Dark Olive Green 38
    '#00CED1', // Dark Turquoise 39
    '#FF1493' // Deep Pink
]



var displayPlotToolbar = function(toolbarDiv,populationDiv,scatterData) {
    scatterData['columnHeadings'].map(function(value,index) {
        $('#xAxisMarker')
            .append($("<option></option>")
            .attr("value",index)
            .text(value));

        $('#yAxisMarker')
            .append($("<option></option>")
            .attr("value",index)
            .text(value));

        $('#zAxisMarker')
            .append($("<option></option>")
            .attr("value",index)
            .text(value));
    });

    $('#xAxisMarker').select2("val",0);
    $('#yAxisMarker').select2("val",1);
    $('#zAxisMarker').select2("val",2);

    scatterData['populations'].map(function(value,index) {
        $('#populationTable tr')
            .last()
            .after('<tr><td align="center"><input type="checkbox" checked class="pop" value=' + value + '/></td><td>' + value + '<td><span style="background-color:' + color_palette[value] + '">&nbsp;&nbsp;&nbsp</span></td></td><td>' + scatterData['percent'][value - 1] + '<td></tr>');
    });

    return;
};


var displayScatterPlot = function() {
    $('#scatterPlotDiv').empty();

    renderer = null;
    scene = null;
    camera = null;
    scatterPlot = null;

    setupRenderer("#scatterPlotDiv");
    setupCamera();
    setupScene();
    function v(x,y,z) {
        return new THREE.Vector3(x,y,z);
    }

    var xExtent = d3.extent(scatterData['xData'], function (d) {return d }),
        yExtent = d3.extent(scatterData['yData'], function (d) {return d }),
        zExtent = d3.extent(scatterData['zData'], function (d) {return d });

    var m = d3.max([xExtent[1],yExtent[1],zExtent[1]])
    var xExtent = [0,m];
    var yExtent = [0,m];
    var zExtent = [0,m];
    console.log("M: ",m);

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
    scatterPlot.add(line);
    var line = new THREE.Line(lineGeoY, lineMat);
    line.type = THREE.Lines;
    scatterPlot.add(line);
    var line = new THREE.Line(lineGeoZ, lineMat);
    line.type = THREE.Lines;
    scatterPlot.add(line);

    var pointCount = scatterData['xData'].length;
    var geometry = new THREE.BufferGeometry();
    var positions = new Float32Array( pointCount * 3 );
    var colors = new Float32Array( pointCount * 3);
    var col = new THREE.Color("steelblue");
    var scale = 2;
    for ( var i = 0; i < pointCount; i++ ) {
        var start = i * 3;
        var x = xScale(scatterData['xData'][i]);
        var y = yScale(scatterData['yData'][i]);
        var z = zScale(scatterData['zData'][i]);
        positions[start] = x;
        positions[start + 1] = y;
        positions[start + 2] = z;
    }


    for ( var i = 0; i < pointCount; i++) {
        j = i * 3;
        //colors[j] = col.r;
        //colors[j+1] = col.g;
        //colors[j+2] = col.b;
        var col = new THREE.Color(color_palette[scatterData['popData'][i]]);
        colors[j] = col.r;
        colors[j+1] = col.g;
        colors[j+2] = col.b;
    }
    geometry.addAttribute( 'position', new THREE.BufferAttribute( positions, 3 ) );
    geometry.addAttribute( 'color', new THREE.BufferAttribute( colors, 3 ) );
    geometry.computeBoundingSphere();
    var pcmaterial = new THREE.PointsMaterial( { size: scale, vertexColors: THREE.VertexColors } );
    var particleSystem = new THREE.Points( geometry, pcmaterial );
    scatterPlot.add( particleSystem );

    renderer.render(scene,camera);
    var paused = false;
    var last = new Date().getTime();
    var down = false;
    var sx = 0,
        sy = 0;

    $('#scatterPlotDiv').on('mousedown',function(ev) {
        down = true;
        sx = ev.clientX;
        sy = ev.clientY;
    });
    $('#scatterPlotDiv').on('mouseup',function() {
        down = false;
    });
    $('#scatterPlotDiv').on('mousemove',function(ev) {
        if (down) {
            var dx = ev.clientX - sx;
            var dy = ev.clientY - sy;
            scatterPlot.rotation.y += dx * 0.01;
            camera.position.y += dy;
            sx += dx;
            sy += dy;
        }
    });
    var animating = false;
    $('#scatterPlotDiv').on('dblclick',function() {
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
            renderer.clear();
            camera.lookAt(scene.position);
            renderer.render(scene, camera);
        }
        window.requestAnimationFrame(animate, renderer.domElement);
    };
    animate(new Date().getTime());
    onmessage = function(ev) {
        paused = (ev.data == 'pause');
    };
}

var processScatterPlotData = function(scatterData) {
    var min = d3.min(scatterData['data'], function(array) {
      return d3.min(array);
    });
    var max = d3.max(scatterData['data'], function(array) {
      return d3.max(array);
    });
    scatterData['min'] = 0;
    scatterData['max'] = 1024;

    var col1 = scatterData['data'].map(function(value,index) {
               return value[scatterData['m1']];});
    var col2 = scatterData['data'].map(function(value,index) {
               return value[scatterData['m2']];});
    var col3 = scatterData['data'].map(function(value,index) {
               return value[scatterData['m3']];});
    var pop = scatterData['data'].map(function(value,index) {
               return value[scatterData['popCol']];});

    var xData = [];
    var yData = [];
    var zData = [];
    var popData = [];
    for (var i = 0; i < col1.length; i++) {
        if (scatterData['populations'].indexOf(pop[i]) >= 0) {
            xData.push(col1[i]);
            yData.push(col2[i]);
            zData.push(col3[i]);
            popData.push(pop[i]);
        }
    }
    scatterData['xData'] = xData;
    scatterData['yData'] = yData;
    scatterData['zData'] = zData;
    scatterData['popData'] = popData;
    return scatterData;
};


function setupRenderer(element) {
    var h = $(window).height() - 200;
    $(element).empty();
    $(element).height(h);
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
        renderer = new THREE.WebGLRenderer( {antialias: true} );
    } else {
        renderer = new THREE.CanvasRenderer();
    }
    test_canvas = undefined;

    renderer.setSize( canvasWidth, canvasHeight );
    renderer.setClearColor(0xEEEEEE, 1.0);
    $(element).append( renderer.domElement );
}

function setupScene() {
    scene = new THREE.Scene();
    scatterPlot = new THREE.Object3D();
    scene.add(scatterPlot);
    //scatterPlot.rotation.y = 0;
}

function setupCamera() {
    camera = new THREE.PerspectiveCamera(50, canvasWidth/canvasHeight, 1, 10000);
    camera.position.z = 250;
    //camera.position.x = -100;
    //camera.position.y = 100;
}
