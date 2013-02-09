(function() {
	var lang = {
		decimalPoint: ',',
		downloadJPEG: 'Scarica immagine JPEG',
		downloadPDF: 'Scarica documento PDF',
		downloadPNG: 'Scarica immagine PNG',
		downloadSVG: 'Scarica immagine SVG',
		exportButtonTitle: 'Esporta...',
		loading: 'Caricamento in corso...',
		months: ['Gennaio', 'Febbraio', 'Marzo', 'Aprile', 'Maggio', 'Giugno', 'Luglio', 'Agosto', 'Settembre', 'Ottobre', 'Novembre', 'Dicembre'],
		printButtonTitle: 'Stampa',
		rangeSelectorFrom: 'Da',
		rangeSelectorTo: 'A',
		rangeSelectorZoom: '',
		resetZoom: '',
		resetZoomTitle: '',
		thousandsSep: '',
		weekdays: ['Domenica', 'Lunedì', 'Martedì', 'Mercoledì', 'Giovedì', 'Venerdì', 'Sabato'],
		nodeshot: {
			active: 'Attivi',
			potential: 'Potenziali',
			hotspot: 'Hotspot',
			links: 'Link',
			km: 'Km',
			yAxis: [ 'Nodi', 'Link', 'Km' ]
		}
	};

	Highcharts.setOptions({ lang: lang });

	function NodeshotStats(container_id) {
		this.CONTAINER_ID = container_id;
		this.data = { links: [], km: [], active: [], potential: [], hotspot: [] };
		this.extremes = [(new Date()).valueOf() - 1000*60*60*24*30*3, (new Date()).valueOf()];

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
			//title: { text: 'Stats' },
			yAxis: [
				{
					title: { text: lang.nodeshot.yAxis[0] },
					height: 200,
					lineWidth: 2
				},
				{
					title: { text: lang.nodeshot.yAxis[1] },
					top: 280,
					height: 100,
					offset: 0,
					lineWidth: 2
				},
				{
					title: { text: lang.nodeshot.yAxis[2] },
					top: 395,
					height: 100,
					offset: 0,
					lineWidth: 2
				}
			],
			series: this.series
		});

		this.refresh = function() {
			var self = this;
			self.highstock.showLoading();

			$.getJSON('http://map.ninux.org/stats.json?callback=?', function(result) {
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
	}

	window.NodeshotStats = NodeshotStats;
})();
