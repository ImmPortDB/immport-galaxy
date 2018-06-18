function CanvasManager(app, canvas_viewport, overview) {
    this.app = app;
    this.cv = canvas_viewport;
    this.cc = this.cv.find("#canvas-container");
    this.overview = overview;
    this.oc = overview.find("#overview-canvas");
    this.ov = overview.find("#overview-viewport");
    // Make overview box draggable
    this.init_drag();
    // Initialize Copy & Paste events
    this.init_copy_paste();
}
$.extend(CanvasManager.prototype, {
    init_drag: function() {
        var self = this;
        var move = (x, y) => {
            x = Math.min(x, self.cv.width() / 2);
            x = Math.max(x, -self.cc.width() + self.cv.width() / 2);
            y = Math.min(y, self.cv.height() / 2);
            y = Math.max(y, -self.cc.height() + self.cv.height() / 2);
            self.cc.css({
                left: x,
                top: y
            });
            self.cv.css({
                "background-position-x": x,
                "background-position-y": y
            });
            self.update_viewport_overlay();
        };
        // Dragging within canvas background
        this.cc.each(function() {
            this.scroll_panel = new ScrollPanel(this);
        });
        var x_adjust;
        var y_adjust;
        this.cv
            .bind("click", function() {
                document.activeElement.blur();
            })
            .bind("dragstart", function() {
                var o = $(this).offset();
                var p = self.cc.position();
                y_adjust = p.top - o.top;
                x_adjust = p.left - o.left;
            })
            .bind("drag", (e, d) => {
                move(d.offsetX + x_adjust, d.offsetY + y_adjust);
            })
            .bind("dragend", () => {
                self.app.workflow.fit_canvas_to_nodes();
                self.draw_overview();
            });
        this.overview.click(e => {
            if (self.overview.hasClass("blockaclick")) {
                self.overview.removeClass("blockaclick");
            } else {
                var in_w = self.cc.width();
                var in_h = self.cc.height();
                var o_w = self.oc.width();
                var o_h = self.oc.height();

                var new_x_offset = e.pageX - self.oc.offset().left - self.ov.width() / 2;

                var new_y_offset = e.pageY - self.oc.offset().top - self.ov.height() / 2;

                move(-(new_x_offset / o_w * in_w), -(new_y_offset / o_h * in_h));
                self.app.workflow.fit_canvas_to_nodes();
                self.draw_overview();
            }
        });
        // Dragging for overview pane
        this.ov
            .bind("drag", (e, d) => {
                var in_w = self.cc.width();
                var in_h = self.cc.height();
                var o_w = self.oc.width();
                var o_h = self.oc.height();
                var new_x_offset = d.offsetX - self.overview.offset().left;
                var new_y_offset = d.offsetY - self.overview.offset().top;
                move(-(new_x_offset / o_w * in_w), -(new_y_offset / o_h * in_h));
            })
            .bind("dragend", () => {
                self.overview.addClass("blockaclick");
                self.app.workflow.fit_canvas_to_nodes();
                self.draw_overview();
            });
        // Dragging for overview border (resize)
        $("#overview-border").bind("drag", function(e, d) {
            var op = $(this).offsetParent();
            var opo = op.offset();
            var new_size = Math.max(op.width() - (d.offsetX - opo.left), op.height() - (d.offsetY - opo.top));
            $(this).css({
                width: new_size,
                height: new_size
            });
            self.draw_overview();
        });

        /*  Disable dragging for child element of the panel so that resizing can
                only be done by dragging the borders */
        $("#overview-border div").bind("drag", () => {});
    },
    init_copy_paste: function() {
        document.addEventListener("copy", e => {
            // If it appears that the user is trying to copy/paste text, we
            // pass that through.
            if (window.getSelection().toString() === "") {
                if (this.app.workflow.active_node && this.app.workflow.active_node.type !== "subworkflow") {
                    e.clipboardData.setData(
                        "application/json",
                        JSON.stringify({
                            nodeId: this.app.workflow.active_node.id
                        })
                    );
                }
                e.preventDefault();
            }
        });

        document.addEventListener("paste", e => {
            // If it appears that the user is trying to paste into a text box,
            // pass that through and skip the workflow copy/paste logic.
            if (
                document.activeElement &&
                document.activeElement.type !== "textarea" &&
                document.activeElement.type !== "text"
            ) {
                var nodeId;
                try {
                    nodeId = JSON.parse(e.clipboardData.getData("application/json")).nodeId;
                } catch (error) {}
                if (nodeId && this.app.workflow.nodes.hasOwnProperty(nodeId)) {
                    this.app.workflow.nodes[nodeId].clone();
                }
                e.preventDefault();
            }
        });
    },
    update_viewport_overlay: function() {
        var cc = this.cc;
        var cv = this.cv;
        var oc = this.oc;
        var ov = this.ov;
        var in_w = cc.width();
        var in_h = cc.height();
        var o_w = oc.width();
        var o_h = oc.height();
        var cc_pos = cc.position();
        ov.css({
            left: -(cc_pos.left / in_w * o_w),
            top: -(cc_pos.top / in_h * o_h),
            // Subtract 2 to account for borders (maybe just change box sizing style instead?)
            width: cv.width() / in_w * o_w - 2,
            height: cv.height() / in_h * o_h - 2
        });
    },
    draw_overview: function() {
        var canvas_el = $("#overview-canvas");

        var size = canvas_el
            .parent()
            .parent()
            .width();

        var c = canvas_el.get(0).getContext("2d");
        var in_w = $("#canvas-container").width();
        var in_h = $("#canvas-container").height();
        var o_h;
        var shift_h;
        var o_w;
        var shift_w;
        // Fit canvas into overview area
        var cv_w = this.cv.width();
        var cv_h = this.cv.height();
        if (in_w < cv_w && in_h < cv_h) {
            // Canvas is smaller than viewport
            o_w = in_w / cv_w * size;
            shift_w = (size - o_w) / 2;
            o_h = in_h / cv_h * size;
            shift_h = (size - o_h) / 2;
        } else if (in_w < in_h) {
            // Taller than wide
            shift_h = 0;
            o_h = size;
            o_w = Math.ceil(o_h * in_w / in_h);
            shift_w = (size - o_w) / 2;
        } else {
            // Wider than tall
            o_w = size;
            shift_w = 0;
            o_h = Math.ceil(o_w * in_h / in_w);
            shift_h = (size - o_h) / 2;
        }
        canvas_el.parent().css({
            left: shift_w,
            top: shift_h,
            width: o_w,
            height: o_h
        });
        canvas_el.attr("width", o_w);
        canvas_el.attr("height", o_h);
        // Draw overview
        $.each(this.app.workflow.nodes, (id, node) => {
            c.fillStyle = "#D2C099";
            c.strokeStyle = "#D8B365";
            c.lineWidth = 1;
            var node_element = $(node.element);
            var position = node_element.position();
            var x = position.left / in_w * o_w;
            var y = position.top / in_h * o_h;
            var w = node_element.width() / in_w * o_w;
            var h = node_element.height() / in_h * o_h;
            if (node.errors) {
                c.fillStyle = "#FFCCCC";
                c.strokeStyle = "#AA6666";
            } else if (node.workflow_outputs !== undefined && node.workflow_outputs.length > 0) {
                c.fillStyle = "#E8A92D";
                c.strokeStyle = "#E8A92D";
            }
            c.fillRect(x, y, w, h);
            c.strokeRect(x, y, w, h);
        });
        this.update_viewport_overlay();
    }
});

// FIXME: merge scroll panel into CanvasManager, clean up hardcoded stuff.
function ScrollPanel(panel) {
    this.panel = panel;
}
$.extend(ScrollPanel.prototype, {
    test: function(e, onmove) {
        clearTimeout(this.timeout);
        var x = e.pageX;
        var y = e.pageY;

        var // Panel size and position
        panel = $(this.panel);

        var panel_pos = panel.position();
        var panel_w = panel.width();
        var panel_h = panel.height();

        var // Viewport size and offset
        viewport = panel.parent();

        var viewport_w = viewport.width();
        var viewport_h = viewport.height();
        var viewport_offset = viewport.offset();

        var // Edges of viewport (in page coordinates)
        min_x = viewport_offset.left;

        var min_y = viewport_offset.top;
        var max_x = min_x + viewport.width();
        var max_y = min_y + viewport.height();

        var // Legal panel range
        p_min_x = -(panel_w - viewport_w / 2);

        var p_min_y = -(panel_h - viewport_h / 2);
        var p_max_x = viewport_w / 2;
        var p_max_y = viewport_h / 2;

        var // Did the panel move?
        moved = false;

        var // Constants
        close_dist = 5;

        var nudge = 23;
        var t = 0;
        if (x - close_dist < min_x) {
            if (panel_pos.left < p_max_x) {
                t = Math.min(nudge, p_max_x - panel_pos.left);
                panel.css("left", panel_pos.left + t);
                moved = true;
            }
        } else if (x + close_dist > max_x) {
            if (panel_pos.left > p_min_x) {
                t = Math.min(nudge, panel_pos.left - p_min_x);
                panel.css("left", panel_pos.left - t);
                moved = true;
            }
        } else if (y - close_dist < min_y) {
            if (panel_pos.top < p_max_y) {
                t = Math.min(nudge, p_max_y - panel_pos.top);
                panel.css("top", panel_pos.top + t);
                moved = true;
            }
        } else if (y + close_dist > max_y) {
            if (panel_pos.top > p_min_y) {
                t = Math.min(nudge, panel_pos.top - p_min_x);
                panel.css("top", `${panel_pos.top - t}px`);
                moved = true;
            }
        }
        if (moved) {
            // Keep moving even if mouse doesn't move
            onmove();
            this.timeout = setTimeout(() => {
                this.test(e, onmove);
            }, 50);
        }
    },
    stop: function() {
        clearTimeout(this.timeout);
    }
});
export default CanvasManager;
