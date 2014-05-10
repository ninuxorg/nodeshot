var NodeRowView = Backbone.Marionette.ItemView.extend({
  tagName: "tr",
  template: "#node-list-row-template"
});

var NodeEmptyView = Backbone.Marionette.ItemView.extend({
    tagName: "tr",
    template: "#node-list-empty-template"
});


var NodeListView = Backbone.Marionette.CompositeView.extend({
    name: 'NodeListView',
    tagName: 'article',
    className: 'center-stage',
    id: 'node-list',
    template: '#node-list-template',
    itemView: NodeRowView,
    itemViewContainer: '#js-rows',
    emptyView: NodeEmptyView,
    
    ui:{
        'searchInput': '#js-search input',
        'filterPanel': '#js-filter-panel',
        'footer': 'footer.fixedbottom '
    },
    
    events:{
        'click .not-implemented': 'notImplemented',
        'submit #js-search': 'search',
        'click #js-reset-filter': 'resetFilter',
        'click #js-open-filter-panel': 'openFilterPanel',
        'click #js-add-node': 'addNode',
        'click #js-next-page': 'getNextPage',
        'click #js-previous-page': 'getPreviousPage',
        'change #js-page-size .selectpicker': 'setPageSize'
    },
    
    collectionEvents: {
        'sync': 'render'
    },
    
    initialize: function(){
        // bind custom resize event
        $(window).on("resize.nodelist", _.bind(this.adjustFooter, this));
        // tell to NodeDetailView to come back here when closing
        Nodeshot.onNodeClose = '#/nodes';
        // mark nodes menu link as active
        $('#nav-bar a[href="#/nodes"]').addClass('active');
    },
    
    onClose: function () {
        // unbind custom resize event
        $(window).off("resize.nodelist");
    },
    
    onDomRefresh: function(){
        $('.selectpicker').selectpicker({
            style: 'btn-special'
        });
        
        $('.hastip').tooltip();
        
        this.adjustFooter();
    },
    
    serializeData: function(){
        return {
            'total': this.model.get('total'),
            'collection': this.collection
        }
    },
    
    /* --- layout --- */
    
    adjustFooter: function(){
        this.ui.footer.css({
            'margin-left': -1 * (($('#body').width() - $('article.center-stage').width()) / 2)
        });
    },
    
    /* --- user interaction --- */
    
    notImplemented: function(e){
        e.preventDefault();
        e.stopPropagation();
        createModal({ message: 'Not implemented yet' });
    },
    
    search: function(e){
        e.preventDefault();
        
        this.collection.search(this.ui.searchInput.val())
        .done(function(){
            var input = $('#js-search input');
            input.trigger('focus').val(input.val());
        });
    },
    
    openFilterPanel: function(e){
        var panel = this.ui.filterPanel,
            self = this;
        
        panel.fadeIn(25, function(){
            // clicking anywhere else closes the panel
            $('html').on('click', function(e){
                if($(e.target).parents('.filter-panel').length === 0){
                    panel.hide();
                    $('html').unbind('click')
                }
                else{
                    panel.hide();
                    self.notImplemented(e);
                }
            });
        });
    },
    
    resetFilter: function(e){
        e.preventDefault();
        this.ui.searchInput.val('');
        this.search(e);
    },
    
    addNode: function(){
        NodeshotController.getMap();
        $('#map-toolbar .icon-pin-add').trigger('click');
    },
    
    /* --- pagination methods --- */
    
    getNextPage: function(e){
        e.preventDefault();
        this.collection.getNextPage();
    },
    
    getPreviousPage: function(e){
        e.preventDefault();
        this.collection.getPreviousPage();
    },
    
    setPageSize: function(e){
        this.collection.setPageSize(parseInt($(e.target).val()));
    }
});
