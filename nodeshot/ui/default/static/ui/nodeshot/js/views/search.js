(function(){
    'use strict';

    var ItemView = Marionette.ItemView.extend({
        tagName: "li",
        template: "#search-result-template"
    });

    var EmptyView = Marionette.ItemView.extend({
        tagName: "li",
        template: '#search-empty-template'
    });

    Ns.views.Search = Marionette.CompositeView.extend({
        tagName: 'div',
        template: '#search-template',
        childView: ItemView,
        childViewContainer: '#js-search-results',
        emptyView: EmptyView,

        ui: {
            'input': 'input',
            'loading': '.animate-spin',
            'icon': '.icon-search',
            'results': 'ul'
        },

        events:{
            'keyup input': 'keyupOnSearch',
            'mouseover ul': 'removeArtificialFocus',
            'click a': 'getResult'
        },

        collectionEvents: {
            'sync': 'render'
        },

        /**
         * local cache methods
         */
        cache: {},

        setCache: function (key, value) {
            if (value instanceof Ns.collections.Search){
                this.cache[key] = value.clone();
            }
        },

        getCache: function (key) {
            if (typeof this.cache[key] === 'undefined') {
                return null;
            }
            return this.cache[key];
        },

        initialize: function(){
            this.collection = new Ns.collections.Search();
            this.render();
            // set max width of dropdown result box on init and on window resize
            this.setResultsMaxWidth();
            $(window).on('resize.search', _.bind(this.setResultsMaxWidth, this));
        },

        /* --- layout --- */

        startSpinning: function () {
            this.ui.icon.hide();
            this.ui.loading.fadeIn(255);
        },

        stopSpinning: function () {
            this.ui.loading.hide();
            this.ui.icon.fadeIn(255);
        },

        setResultsMaxWidth: function () {
            // determine max width for results dropdown
            var maxWidth = $(window).width() - this.ui.input.offset().left - 10;
            this.ui.results.css('max-width', maxWidth);
        },

        showResults: function(){
            var self = this;
            // unbind any previously bound custom keydown event
            $(window).off('keydown.search');
            // bind to custom keydown event
            $(window).on('keydown.search', _.bind(this.keydown, this));
            // show results
            this.ui.results.fadeIn(255);
            // bind click on entire page
            $('html').on('click.search', function(e){
                // if clicking outside hide
                if(!$(e.target).parents('#general-search').length){
                    self.hideResults();
                    $('html').unbind('click.search');
                }
            })
        },

        hideResults: function(){
            this.ui.results.hide();
            // unbind keydown event
            $(window).off('keydown.search');
        },

        removeArtificialFocus: function(e){
            $('#js-search-results a.focus').removeClass('focus').trigger('blur');
        },

        /* --- user interaction --- */

        keyupOnSearch: function(e){
            // ENTER
            if (e.keyCode === 13) {
                this.search(e.target.value);
            }
            // ESC
            else if(e.keyCode === 27){
                this.stopSpinning();
                this.hideResults();
            }
        },

        search: function(q){
            var self = this,
                clone = this.collection.clone(),
                cache = this.getCache(q);
            if (cache !== null) {
                this.collection.reset(cache.models);
                self.showResults();
                return;
            }
            // show loading indicator
            this.startSpinning();
            // reset any previous results
            this.collection.reset();
            // fetch results in cloned collection so that eventual address results might not be erased
            clone.search(q).done(function(){
                self.collection.add(clone.models);
                self.setCache(q, self.collection);
                // hide loading indicator
                self.stopSpinning();
                self.showResults();
                // keep word
                self.ui.input.trigger('focus').val(q);
            });
            this.searchAddress(q);
        },

        searchAddress: function (q) {
            // query must be longer than 10 characters
            if (q.length > 10 && _.containsAny(q, Ns.settings.addressSearchTriggers)) {
                var addresses = $.geocode({ q: q });
                addresses = new Ns.collections.Search(addresses);
                this.collection.add(addresses.models);
                this.setCache(q, this.collection);
            }
        },

        keydown: function(e){
            if(this.ui.results.is(':hidden')){
                return
            }
            // Must be before down commands because of shift + tab
            // Page up, Up arrow, Up numpad, Page-up numpad or shift + tab
            if(_.contains([33, 38, 104, 105], e.keyCode) || (e.shiftKey && e.keyCode === 9)){
                this.moveThroughResults('up', e);
            }
            // Tab, Page down, Down arrow, Down numpad, Page-down numpad
            else if(_.contains([9, 34, 40, 98, 99], e.keyCode)){
                this.moveThroughResults('down', e);
            }
            // Home gets first
            else if(e.keyCode === 36) {
                this.moveThroughResults('home', e);
            }
            else if(e.keyCode === 35) {
                this.moveThroughResults('end', e);
            }
            // ESC
            else if(e.keyCode === 27){
                this.ui.input.focus();
                this.keyupOnSearch(e);
            }
            // in all the other cases user is probably typing / deleting
            // except if pressing shift or enter
            else if (!e.shiftKey && e.keyCode != 13) {
                this.ui.input.focus();
                this.removeArtificialFocus();
            }
        },

        moveThroughResults: function(direction, e){
            e.preventDefault();
            e.stopPropagation();
            var prevOrNext = direction === 'down' ? 'next' : 'prev',
                homeOrEnd = direction === 'home' ? 0 : -1,
                current = this.$('a.focus'),
                a;
            // remove any focus
            current.removeClass('focus');
            // if no element wifh focus go to first result
            if (!current.length) {
                this.$('a').eq(0)
                    .addClass('focus').focus();
            }
            // if up or down
            else if (_.contains(['down', 'up'], direction)){
                a = current.eq(0).parent()[prevOrNext]().find('a');
                // if any next or prev move focus
                if (a.length) {
                    a.addClass('focus').focus();
                }
                // if no prev and going up move focus to input
                else if (direction === 'up') {
                    this.ui.input.focus();
                }
            }
            // home or end
            else {
                this.$('a').eq(homeOrEnd).addClass('focus').focus();
            }
        },

        getResult: function(e){
            if($(e.target).hasClass('empty')){
                e.preventDefault();
            }
            this.hideResults();
        }
    });
})();
