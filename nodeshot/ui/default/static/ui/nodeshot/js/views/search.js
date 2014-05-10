var SearchResultView = Backbone.Marionette.ItemView.extend({
    tagName: "li",
    template: "#search-result-template"
});

var SearchEmptyView = Backbone.Marionette.ItemView.extend({
    tagName: "li",
    template: '#search-empty-template'
});

var SearchView = Backbone.Marionette.CompositeView.extend({
    name: 'SearchView',
    el: '#general-search',
    tagName: 'div',
    template: '#search-template',
    itemView: SearchResultView,
    itemViewContainer: '#js-search-results',
    emptyView: SearchEmptyView,
    
    ui: {
        'input': 'input',
        'loading': '.animate-spin',
        'icon': '.icon-search',
        'results': 'ul'
    },
    
    events:{
        'keyup input': 'keyupOnSearch',
        'mouseover ul': 'removeArtificialFocus',
        'click a': 'getNode'
    },
    
    collectionEvents: {
        'sync': 'render'
    },
    
    initialize: function(){
        this.collection = new NodeCollection();
        this.render();
        // bind to keydown event
        $(window).on('keydown', _.bind(this.keydown, this));
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
    
    showResults: function(){
        var self = this;
        this.ui.results.fadeIn(255);
        
        $('html').on('click.search', function(e){
            // if clicking outside
            if(!$(e.target).parents('#general-search').length){
                self.hideResults();
                $('html').unbind('click.search');
            }
        })
    },
    
    hideResults: function(){
        this.ui.results.hide();
    },
    
    removeArtificialFocus: function(e){
        $('#js-search-results a.focus').removeClass('focus').trigger('blur');
    },
    
    /* --- user interaction --- */
    
    keyupOnSearch: function(e){
        if (e.keyCode === 13) {
            this.search(e.target.value);
        }
        else if(e.keyCode === 27){
            this.ui.input.trigger('blur');
            this.stopSpinning();
            this.hideResults();
        }
    },
    
    search: function(q){
        var self = this;
        
        // show loading indicator
        this.startSpinning();
        
        // fetch results
        this.collection.search(q)
        .done(function(){
            // hide loading indicator
            self.stopSpinning();
            self.showResults();
            // keep word
            self.ui.input.trigger('focus').val(q);
        });
    },
    
    keydown: function(e){
        if(this.ui.results.is(':hidden')){
            return
        }
        if(e.keyCode == 40){
            this.moveThroughResults('down', e);
        }
        else if(e.keyCode == 38){
            this.moveThroughResults('up', e);
        }
    },
    
    moveThroughResults: function(direction, e){
        e.preventDefault();
        e.stopPropagation();
        
        var method = direction === 'down' ? 'next' : 'prev',
            current = $('#js-search-results a.focus');
        
        // remove any focus
        current.removeClass('focus');
        
        if(!current.length){
            $('#js-search-results a').eq(0)
                .addClass('focus').focus();
        }
        else{
            current.eq(-1)
                .parent()[method]()
                .find('a')
                .addClass('focus').focus();
        }
    },
    
    getNode: function(e){
        if($(e.target).hasClass('empty')){
            e.preventDefault();
        }
        this.hideResults();
    }
});
