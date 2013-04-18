(function() {

	var lang = NS_STATS_CONFIG['lang']
	Highcharts.setOptions({ lang: lang });

	function NodeshotStats(container_id) {
		this.CONTAINER_ID = container_id;
		this.data = { links: [], km: [], active: [], potential: [], hotspot: [] };
		this.extremes = [(new Date()).valueOf() - 1000*60*60*24*30*3, (new Date()).valueOf()];

		this.yAxis = [
			{
				title: { text: lang.nodeshot.yAxis[0] },
				top: 35,
				height: 200,
				lineWidth: 2,
				showEmpty: false
			},
			{
				title: { text: lang.nodeshot.yAxis[1] },
				top: 260,
				height: 100,
				offset: 0,
				lineWidth: 2,
				showEmpty: false
			},
			{
				title: { text: lang.nodeshot.yAxis[2] },
				top: 385,
				height: 100,
				offset: 0,
				lineWidth: 2,
				showEmpty: false
			}
		];

		this.series = [
			{
				type: 'line',
				name: lang.nodeshot.active,
				key: 'active',
				data: [],
				dataGrouping: { units: groupingUnits }
			},
			{
				type: 'line',
				name: lang.nodeshot.potential,
				key: 'potential',
				data: [],
				dataGrouping: { units: groupingUnits }
			},
			{
				type: 'line',
				name: lang.nodeshot.hotspot,
				key: 'hotspot',
				data: [],
				dataGrouping: { units: groupingUnits }
			},
			{
				type: 'line',
				name: lang.nodeshot.links,
				key: 'links',
				data: [],
				yAxis: 1,
				dataGrouping: { units: groupingUnits }
			},
			{
				type: 'line',
				name: lang.nodeshot.km,
				key: 'km',
				data: [],
				yAxis: 2,
				dataGrouping: { units: groupingUnits }
			}
		];

		// set the allowed units for data grouping
		var groupingUnits = [
			[
				'week',                         // unit name
				[1]                             // allowed multiples
			],
			[
				'month',
				[1, 2, 3, 4, 6]
			]
		];

		// parse a date in dd-mm-yyyy format
		function parseDate(input) {
			var parts = input.match(/(\d+)/g);
			return new Date(parts[2], parts[1]-1, parts[0]);
		}

		this.highstock = new Highcharts.StockChart({
			chart: {
				renderTo: this.CONTAINER_ID,
				alignTicks: false
			},
			rangeSelector: { buttons: [] },
			yAxis: this.yAxis,
			series: this.series
		});

		this.refresh = function() {
			var self = this;
			self.highstock.showLoading();

			$.getJSON(NS_STATS_CONFIG['url'], function(result) {
				var raw = result.info, dataLength = raw.length;
				//pulizia
				$.each(self.data, function(key) {
					self.data[key] = [];
				});
				//riempimento
				for (i = 0; i < dataLength; i++) {
					var date = parseDate(raw[i].date).valueOf();
					$.each(self.data, function(key) {
						self.data[key].push([ date, raw[i][key] ]);
					});
				}
				for (var index in self.series) {
					var key = self.series[index].key;
					self.highstock.series[index].setData(self.data[key], false);
				}
				self.highstock.xAxis[0].setExtremes(self.extremes[0], self.extremes[1], false);
				self.highstock.redraw();
				self.highstock.hideLoading();
			});
		}

		// this function works in three modes:
		// 1. calling with two parameters: passed directly to Highstock
		// 2. calling with one parameter: makes the "window" from x seconds ago to now
		// 3. calling with no parameters: makes the "window" to the whole collection of data
		this.setExtremes = function(from, to) {
			if (to) {
				this.extremes[0] = from;
				this.extremes[1] = to;
			}
			else if (from) {
				this.extremes[0] = (new Date()).valueOf() - from*1000;
				this.extremes[1] = (new Date()).valueOf();
			}
			else {
				var extr = this.highstock.xAxis[0].getExtremes();
				this.extremes[0] = extr.dataMin;
				this.extremes[1] = extr.dataMax;
			}
			this.highstock.xAxis[0].setExtremes(this.extremes[0], this.extremes[1]);
		}

		this._getSerie = function(key) {
			for (var index in this.series)
				if (this.series[index].key == key)
					return index;
		}

	/*
		this._checkAxis = function() {
			for (var i in this.highstock.yAxis)
				this.highstock.yAxis[i].visible = false;
			for (var i in this.highstock.series)
				if (this.highstock.series[i].visible)
					this.highstock.series[i].yAxis.visible = true;
			for (var i = 0; i < this.highstock.yAxis.length; i++) {
				if (!this.highstock.yAxis[i].visible) {
					if (i == 0) {
						var newh = this.highstock.yAxis[i].height;
						for (var j = i+1; j < this.highstock.yAxis.length; j++) {
							console.log(j, this.highstock.yAxis[j]);
							if (!this.highstock.yAxis[j].visible)
								newh = this.highstock.yAxis[j].height + this.highstock.yAxis[j].top;
							else {
								this.highstock.yAxis[j].top = 0;
								this.highstock.yAxis[j].height = newh;
								break;
							}
						}
					}
				}
			}
			this.highstock.redraw();
		}
		*/

		this.showSerie = function(key) {
			var serie = this._getSerie(key);
			if (!serie) return;
			this.highstock.series[serie].show();
			//this._checkAxis();
		}
		this.hideSerie = function(key) {
			var serie = this._getSerie(key);
			if (!serie) return;
			this.highstock.series[serie].hide();
			//this._checkAxis();
		}
		this.toggleSerie = function(key) {
			var serie = this._getSerie(key);
			if (!serie) return;
			if (this.highstock.series[serie].visible)
				this.hideSerie(key);
			else
				this.showSerie(key);
		}
	}

	window.NodeshotStats = NodeshotStats;
})();

$(document).ready(function() {
	var stats = new NodeshotStats('container');
	stats.refresh();

	$('.rangeSelector').click(function(e) {
		var $button = $(this);
		stats.setExtremes($button.attr('data-from'), $button.attr('data-to'));
	});

	$('.toggleSerie').click(function(e) {
		var $button = $(this);
		stats.toggleSerie($button.attr('data-key'));
	});
});