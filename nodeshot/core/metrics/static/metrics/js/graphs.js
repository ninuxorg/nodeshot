(function () {
    'use strict';
    window.Ns = window.Ns || {};

    Ns.graphs = {
        /**
         * Creates nvd3 linear graph
         */
        linear: function (selector, data) {
            nv.addGraph(function () {
                var chart = nv.models.lineChart().useInteractiveGuideline(true);
                chart.xAxis
                    .axisLabel('Datetime')
                    .tickFormat(function (date) {
                        return d3.time.format('%d-%m-%Y')(new Date(date));
                    });
                chart.yAxis
                    .axisLabel('Value')
                    .tickFormat(d3.format('.02f'));
                d3.select(selector)
                    .datum(data)
                    .transition().duration(500)
                    .call(chart);
                nv.utils.windowResize(chart.update);
                return chart;
            });
        },

        /**
         * converts influxdb data in the format expected by d3
         */
        convertInfluxDbData: function (json) {
            var data, key, i, len, index,
                metrics = [],
                values = {},
                graphData = [],
                colors = [
                    '#1f77b4', '#2ca02c', '#ff7f0e', '#de5a5e', '#aec7e8'
                ].reverse();
            // determine numeric data
            for (key in json) {
                if (json.hasOwnProperty(key)) {
                    data = json[key];
                    break;
                }
            }
            // if no data interrupt here
            if (!data) {
                // return empty structure
                return [];
            }
            // prepare structures that will contain data

            for (key in data[0]) {
                if (data[0].hasOwnProperty(key) && key !== 'time') {
                    if (typeof(data[0][key]) === 'number' || data[0][key] === null) {
                        metrics.push(key);
                        values[key] = [];
                    }
                }
            }
            // push data
            for (i=0, len=data.length; i<len; i++) {
                for (index in metrics) {
                    key = metrics[index];
                    values[key].push({
                        y: data[i][key] || 0,
                        x: Date.parse(data[i].time)
                    });
                }
            }
            // prepare final structure for D3
            for (index in metrics) {
                if (colors.length) {
                    key = metrics[index];
                    graphData.push({
                        'key': key,
                        'color': colors.pop(),
                        'values': values[key]
                    });
                }
            }
            return graphData;
        },

        createFromJson: function (type, selector, json) {
            Ns.graphs[type](selector, Ns.graphs.convertInfluxDbData(json));
        },

        init: function () {
            $('.ns-chart').each(function (i, el) {
                var chartDiv = $(el),
                    url = chartDiv.attr('data-url'),
                    type = chartDiv.attr('data-type'),
                    width = chartDiv.attr('data-width'),
                    height = chartDiv.attr('data-height');
                // append svg element
                chartDiv.append('<svg style="height:'+height+';width:'+width+';margin:0 auto" id="ns-chart-' + i + '"></svg>');
                // get graph data
                $.getJSON(url).done(function (json) {
                    // create graph
                    Ns.graphs.createFromJson(type, '#ns-chart-' + i, json);
                });
            });
        }
    };
})();
