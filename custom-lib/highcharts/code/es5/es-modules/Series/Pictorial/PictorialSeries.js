/* *
 *
 *  (c) 2010-2025 Torstein Honsi, Magdalena Gut
 *
 *  License: www.highcharts.com/license
 *
 *  !!!!!!! SOURCE GETS TRANSPILED BY TYPESCRIPT. EDIT TS FILE ONLY. !!!!!!!
 *
 * */
'use strict';
var __extends = (this && this.__extends) || (function () {
    var extendStatics = function (d, b) {
        extendStatics = Object.setPrototypeOf ||
            ({ __proto__: [] } instanceof Array && function (d, b) { d.__proto__ = b; }) ||
            function (d, b) { for (var p in b) if (Object.prototype.hasOwnProperty.call(b, p)) d[p] = b[p]; };
        return extendStatics(d, b);
    };
    return function (d, b) {
        if (typeof b !== "function" && b !== null)
            throw new TypeError("Class extends value " + String(b) + " is not a constructor or null");
        extendStatics(d, b);
        function __() { this.constructor = d; }
        d.prototype = b === null ? Object.create(b) : (__.prototype = b.prototype, new __());
    };
})();
/* *
 *
 *  Imports
 *
 * */
import '../Column/ColumnSeries.js';
import PatternFill from '../../Extensions/PatternFill.js';
import A from '../../Core/Animation/AnimationUtilities.js';
import Chart from '../../Core/Chart/Chart.js';
import PictorialPoint from './PictorialPoint.js';
import PictorialUtilities from './PictorialUtilities.js';
import Series from '../../Core/Series/Series.js';
import SeriesRegistry from '../../Core/Series/SeriesRegistry.js';
import StackItem from '../../Core/Axis/Stacking/StackItem.js';
import SVGRenderer from '../../Core/Renderer/SVG/SVGRenderer.js';
import U from '../../Core/Utilities.js';
var ColumnSeries = SeriesRegistry.seriesTypes.column;
PatternFill.compose(Chart, Series, SVGRenderer);
var animObject = A.animObject;
var getStackMetrics = PictorialUtilities.getStackMetrics, invertShadowGroup = PictorialUtilities.invertShadowGroup, rescalePatternFill = PictorialUtilities.rescalePatternFill;
var addEvent = U.addEvent, defined = U.defined, merge = U.merge, objectEach = U.objectEach, pick = U.pick;
/* *
 *
 *  Class
 *
 * */
/**
 * The pictorial series type.
 *
 * @private
 * @class
 * @name Highcharts.seriesTypes.pictorial
 *
 * @augments Highcharts.Series
 */
var PictorialSeries = /** @class */ (function (_super) {
    __extends(PictorialSeries, _super);
    function PictorialSeries() {
        return _super !== null && _super.apply(this, arguments) || this;
    }
    /* *
     *
     * Functions
     *
     * */
    /* eslint-disable valid-jsdoc */
    /**
     * Animate in the series. Called internally twice. First with the `init`
     * parameter set to true, which sets up the initial state of the
     * animation. Then when ready, it is called with the `init` parameter
     * undefined, in order to perform the actual animation.
     *
     * @function Highcharts.Series#animate
     *
     * @param {boolean} [init]
     * Initialize the animation.
     */
    PictorialSeries.prototype.animate = function (init) {
        var _a = this, chart = _a.chart, group = _a.group, animation = animObject(this.options.animation), 
        // The key for temporary animation clips
        animationClipKey = [
            this.getSharedClipKey(),
            animation.duration,
            animation.easing,
            animation.defer
        ].join(',');
        var animationClipRect = chart.sharedClips[animationClipKey];
        // Initialize the animation. Set up the clipping rectangle.
        if (init && group) {
            var clipBox = chart.getClipBox(this);
            // Create temporary animation clips
            if (!animationClipRect) {
                clipBox.y = clipBox.height;
                clipBox.height = 0;
                animationClipRect = chart.renderer.clipRect(clipBox);
                chart.sharedClips[animationClipKey] = animationClipRect;
            }
            group.clip(animationClipRect);
            // Run the animation
        }
        else if (animationClipRect &&
            // Only first series in this pane
            !animationClipRect.hasClass('highcharts-animating')) {
            var finalBox = chart.getClipBox(this);
            animationClipRect
                .addClass('highcharts-animating')
                .animate(finalBox, animation);
        }
    };
    PictorialSeries.prototype.animateDrilldown = function () { };
    PictorialSeries.prototype.animateDrillupFrom = function () { };
    PictorialSeries.prototype.pointAttribs = function (point) {
        var pointAttribs = _super.prototype.pointAttribs.apply(this, arguments), seriesOptions = this.options, series = this, paths = seriesOptions.paths;
        if (point && point.shapeArgs && paths) {
            var shape = paths[point.index % paths.length], _a = getStackMetrics(series.yAxis, shape), y = _a.y, height = _a.height, pathDef = shape.definition;
            // New pattern, replace
            if (pathDef !== point.pathDef) {
                point.pathDef = pathDef;
                pointAttribs.fill = {
                    pattern: {
                        path: {
                            d: pathDef,
                            fill: pointAttribs.fill,
                            strokeWidth: pointAttribs['stroke-width'],
                            stroke: pointAttribs.stroke
                        },
                        x: point.shapeArgs.x,
                        y: y,
                        width: point.shapeArgs.width || 0,
                        height: height,
                        patternContentUnits: 'objectBoundingBox',
                        backgroundColor: 'none',
                        color: '#ff0000'
                    }
                };
            }
            else if (point.pathDef && point.graphic) {
                delete pointAttribs.fill;
            }
        }
        delete pointAttribs.stroke;
        delete pointAttribs.strokeWidth;
        return pointAttribs;
    };
    /**
     * Make sure that path.max is also considered when calculating dataMax.
     */
    PictorialSeries.prototype.getExtremes = function () {
        var extremes = _super.prototype.getExtremes.apply(this, arguments), series = this, paths = series.options.paths;
        if (paths) {
            paths.forEach(function (path) {
                if (defined(path.max) &&
                    defined(extremes.dataMax) &&
                    path.max > extremes.dataMax) {
                    extremes.dataMax = path.max;
                }
            });
        }
        return extremes;
    };
    /* *
     *
     *  Static Properties
     *
     * */
    PictorialSeries.defaultOptions = merge(ColumnSeries.defaultOptions, 
    /**
     * A pictorial chart uses vector images to represents the data.
     * The shape of the data point is taken from the path parameter.
     *
     * @sample       {highcharts} highcharts/demo/pictorial/
     *               Pictorial chart
     *
     * @extends      plotOptions.column
     * @since 11.0.0
     * @product      highcharts
     * @excluding    allAreas, borderRadius,
     *               centerInCategory, colorAxis, colorKey, connectEnds,
     *               connectNulls, crisp, compare, compareBase, dataSorting,
     *               dashStyle, dataAsColumns, linecap, lineWidth, shadow,
     *               onPoint
     * @requires     modules/pictorial
     * @optionparent plotOptions.pictorial
     */
    {
        borderWidth: 0
    });
    return PictorialSeries;
}(ColumnSeries));
/* *
 *
 *  Events
 *
 * */
addEvent(PictorialSeries, 'afterRender', function () {
    var series = this, paths = series.options.paths, fillUrlMatcher = /url\(([^)]+)\)/;
    series.points.forEach(function (point) {
        if (point.graphic && point.shapeArgs && paths) {
            var shape = paths[point.index % paths.length], fill = point.graphic.attr('fill'), match = fill && fill.match(fillUrlMatcher), _a = getStackMetrics(series.yAxis, shape), y = _a.y, height = _a.height;
            if (match && series.chart.renderer.patternElements) {
                var currentPattern = series.chart.renderer.patternElements[match[1].slice(1)];
                if (currentPattern) {
                    currentPattern.animate({
                        x: point.shapeArgs.x,
                        y: y,
                        width: point.shapeArgs.width || 0,
                        height: height
                    });
                }
            }
            rescalePatternFill(point.graphic, getStackMetrics(series.yAxis, shape).height, point.shapeArgs.width || 0, point.shapeArgs.height || Infinity, series.options.borderWidth || 0);
        }
    });
});
/**
 *
 */
function renderStackShadow(stack) {
    // Get first pictorial series
    var stackKeys = Object
        .keys(stack.points)
        .filter(function (p) { return p.split(',').length > 1; }), allSeries = stack.axis.chart.series, seriesIndexes = stackKeys.map(function (key) {
        return parseFloat(key.split(',')[0]);
    });
    var seriesIndex = -1;
    seriesIndexes.forEach(function (index) {
        if (allSeries[index] && allSeries[index].visible) {
            seriesIndex = index;
        }
    });
    var series = stack.axis.chart.series[seriesIndex];
    if (series &&
        series.is('pictorial') &&
        stack.axis.hasData() &&
        series.xAxis.hasData()) {
        var xAxis = series.xAxis, options = stack.axis.options, chart = stack.axis.chart, stackShadow = stack.shadow, xCenter = xAxis.toPixels(stack.x, true), x = chart.inverted ? xAxis.len - xCenter : xCenter, paths = series.options.paths || [], index = stack.x % paths.length, shape = paths[index], width = series.getColumnMetrics &&
            series.getColumnMetrics().width, _a = getStackMetrics(series.yAxis, shape), height = _a.height, y = _a.y, shadowOptions = options.stackShadow, strokeWidth = pick(shadowOptions && shadowOptions.borderWidth, series.options.borderWidth, 1);
        if (!stackShadow &&
            shadowOptions &&
            shadowOptions.enabled &&
            shape) {
            if (!stack.shadowGroup) {
                stack.shadowGroup = chart.renderer.g('shadow-group')
                    .add();
            }
            stack.shadowGroup.attr({
                translateX: chart.inverted ?
                    stack.axis.pos : xAxis.pos,
                translateY: chart.inverted ?
                    xAxis.pos : stack.axis.pos
            });
            stack.shadow = chart.renderer.rect(x, y, width, height)
                .attr({
                fill: {
                    pattern: {
                        path: {
                            d: shape.definition,
                            fill: shadowOptions.color ||
                                '#dedede',
                            strokeWidth: strokeWidth,
                            stroke: shadowOptions.borderColor ||
                                'transparent'
                        },
                        x: x,
                        y: y,
                        width: width,
                        height: height,
                        patternContentUnits: 'objectBoundingBox',
                        backgroundColor: 'none',
                        color: '#dedede'
                    }
                }
            })
                .add(stack.shadowGroup);
            invertShadowGroup(stack.shadowGroup, stack.axis);
            rescalePatternFill(stack.shadow, height, width, height, strokeWidth);
            stack.setOffset(series.pointXOffset || 0, series.barW || 0);
        }
        else if (stackShadow && stack.shadowGroup) {
            stackShadow.animate({
                x: x,
                y: y,
                width: width,
                height: height
            });
            var fillUrlMatcher = /url\(([^)]+)\)/, fill = stackShadow.attr('fill'), match = fill && fill.match(fillUrlMatcher);
            if (match && chart.renderer.patternElements) {
                chart.renderer.patternElements[match[1].slice(1)]
                    .animate({
                    x: x,
                    y: y,
                    width: width,
                    height: height
                });
            }
            stack.shadowGroup.animate({
                translateX: chart.inverted ?
                    stack.axis.pos : xAxis.pos,
                translateY: chart.inverted ?
                    xAxis.pos : stack.axis.pos
            });
            invertShadowGroup(stack.shadowGroup, stack.axis);
            rescalePatternFill(stackShadow, height, width, height, strokeWidth);
            stack.setOffset(series.pointXOffset || 0, series.barW || 0);
        }
    }
    else if (stack.shadow && stack.shadowGroup) {
        stack.shadow.destroy();
        stack.shadow = void 0;
        stack.shadowGroup.destroy();
        stack.shadowGroup = void 0;
    }
}
/**
 *
 */
function forEachStack(chart, callback) {
    if (chart.axes) {
        chart.axes.forEach(function (axis) {
            if (!axis.stacking) {
                return;
            }
            var stacks = axis.stacking.stacks;
            // Render each stack total
            objectEach(stacks, function (type) {
                objectEach(type, function (stack) {
                    callback(stack);
                });
            });
        });
    }
}
addEvent(Chart, 'render', function () {
    forEachStack(this, renderStackShadow);
});
addEvent(StackItem, 'afterSetOffset', function (e) {
    if (this.shadow) {
        var _a = this.axis, chart = _a.chart, len = _a.len, xOffset = e.xOffset, width = e.width, translateX = chart.inverted ? xOffset - chart.xAxis[0].len : xOffset, translateY = chart.inverted ? -len : 0;
        this.shadow.attr({
            translateX: translateX,
            translateY: translateY
        });
        this.shadow.animate({ width: width });
    }
});
/**
 *
 */
function destroyAllStackShadows(chart) {
    forEachStack(chart, function (stack) {
        if (stack.shadow && stack.shadowGroup) {
            stack.shadow.destroy();
            stack.shadowGroup.destroy();
            delete stack.shadow;
            delete stack.shadowGroup;
        }
    });
}
// This is a workaround due to no implementation of the animation drilldown.
addEvent(Chart, 'afterDrilldown', function () {
    destroyAllStackShadows(this);
});
addEvent(Chart, 'afterDrillUp', function () {
    destroyAllStackShadows(this);
});
PictorialSeries.prototype.pointClass = PictorialPoint;
SeriesRegistry.registerSeriesType('pictorial', PictorialSeries);
/* *
 *
 *  Default Export
 *
 * */
export default PictorialSeries;
/* *
 *
 * API Options
 *
 * */
/**
 * A `pictorial` series. If the [type](#series.pictorial.type) option is not
 * specified, it is inherited from [chart.type](#chart.type).
 *
 * @extends   series,plotOptions.pictorial
 * @since 11.0.0
 * @product   highcharts
 * @excluding dataParser, borderRadius, boostBlending, boostThreshold,
 *            borderColor, borderWidth, centerInCategory, connectEnds,
 *            connectNulls, crisp, colorKey, dataURL, dataAsColumns, depth,
 *            dragDrop, edgeColor, edgeWidth, linecap, lineWidth,  marker,
 *            dataSorting, dashStyle, onPoint, relativeXValue, shadow, zoneAxis,
 *            zones
 * @requires  modules/pictorial
 * @apioption series.pictorial
 */
/**
 * An array of data points for the series. For the `pictorial` series type,
 * points can be given in the following ways:
 *
 * 1. An array of arrays with 2 values. In this case, the values correspond
 *    to `x,y`. If the first value is a string, it is applied as the name
 *    of the point, and the `x` value is inferred. The `x` value can also be
 *    omitted, in which case the inner arrays should be of length 2. Then the
 *    `x` value is automatically calculated, either starting at 0 and
 *    incremented by 1, or from `pointStart` and `pointInterval` given in the
 *    series options.
 *    ```js
 *    data: [
 *        [0, 40],
 *        [1, 50],
 *        [2, 60]
 *    ]
 *    ```
 *
 * 2. An array of objects with named values. The following snippet shows only a
 *    few settings, see the complete options set below. If the total number of
 *    data points exceeds the series'
 *    [turboThreshold](#series.pictorial.turboThreshold), this option is not
 *    available.
 *    ```js
 *    data: [{
 *        x: 0,
 *        y: 40,
 *        name: "Point1",
 *        color: "#00FF00"
 *    }, {
 *        x: 1,
 *        y: 60,
 *        name: "Point2",
 *        color: "#FF00FF"
 *    }]
 *    ```
 *
 * @type      {Array<Array<(number|string),number>|Array<(number|string),number,number>|*>}
 * @extends   series.column.data
 *
 * @sample {highcharts} highcharts/demo/pictorial/
 *         Pictorial chart
 * @sample {highcharts} highcharts/demo/pictorial-stackshadow/
 *         Pictorial stackShadow option
 * @sample {highcharts} highcharts/series-pictorial/paths-max/
 *         Pictorial max option
 *
 * @excluding borderColor, borderWidth, dashStyle, dragDrop
 * @since 11.0.0
 * @product   highcharts
 * @apioption series.pictorial.data
 */
/**
 * The paths include options describing the series image. For further details on
 * preparing the SVG image, please refer to the [pictorial
 * documentation](https://www.highcharts.com/docs/chart-and-series-types/pictorial).
 *
 * @declare   Highcharts.SeriesPictorialPathsOptionsObject
 * @type      {Array<*>}
 *
 * @sample    {highcharts} highcharts/demo/pictorial/
 *            Pictorial chart
 *
 * @since     11.0.0
 * @product   highcharts
 * @apioption series.pictorial.paths
 */
/**
 * The definition defines a path to be drawn. It corresponds `d` SVG attribute.
 *
 * @type      {string}
 *
 * @sample    {highcharts} highcharts/demo/pictorial/
 *            Pictorial chart
 *
 * @product   highcharts
 * @apioption series.pictorial.paths.definition
 */
/**
 * The max option determines height of the image. It is the ratio of
 * `yAxis.max` to the `paths.max`.
 *
 * @sample {highcharts} highcharts/series-pictorial/paths-max
 *         Pictorial max option
 *
 * @type      {number}
 * @default   yAxis.max
 * @product   highcharts
 * @apioption series.pictorial.paths.max
 */
/**
 * Relevant only for pictorial series. The `stackShadow` forms the background of
 * stacked points. Requires `series.stacking` to be defined.
 *
 * @sample {highcharts} highcharts/demo/pictorial-stackshadow/ Pictorial
 *         stackShadow option
 *
 * @declare   Highcharts.YAxisOptions
 * @type      {*}
 * @since 11.0.0
 * @product   highcharts
 * @requires  modules/pictorial
 * @apioption yAxis.stackShadow
 */
/**
 * The color of the `stackShadow` border.
 *
 * @declare   Highcharts.YAxisOptions
 * @type      {Highcharts.ColorString|Highcharts.GradientColorObject|Highcharts.PatternObject}
 * @default   transparent
 * @product   highcharts
 * @requires  modules/pictorial
 * @apioption yAxis.stackShadow.borderColor
 */
/**
 * The width of the `stackShadow` border.
 *
 * @declare   Highcharts.YAxisOptions
 * @type      {number}
 * @default   0
 * @product   highcharts
 * @requires  modules/pictorial
 * @apioption yAxis.stackShadow.borderWidth
 */
/**
 * The color of the `stackShadow`.
 *
 * @declare   Highcharts.YAxisOptions
 * @type      {Highcharts.ColorString|Highcharts.GradientColorObject|Highcharts.PatternObject}
 * @default   #dedede
 * @product   highcharts
 * @requires  modules/pictorial
 * @apioption yAxis.stackShadow.color
 */
/**
 * Enable or disable `stackShadow`.
 *
 * @declare   Highcharts.YAxisOptions
 * @type      {boolean}
 * @default   undefined
 * @product   highcharts
 * @requires  modules/pictorial
 * @apioption yAxis.stackShadow.enabled
 */
''; // Adds doclets above to transpiled file
