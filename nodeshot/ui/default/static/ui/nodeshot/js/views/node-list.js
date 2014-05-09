var NodeRowView = Backbone.Marionette.ItemView.extend({
  tagName: "tr",
  template: "#node-list-row-template"
});

var NodeListView = Backbone.Marionette.CompositeView.extend({
    name: 'NodeListView',
    tagName: 'article',
    className: 'center-stage',
    id: 'node-list',
    template: '#node-list-template',
    itemView: NodeRowView,
    itemViewContainer: '#js-rows',
    
    ui:{
        'filterPanel': '#js-filter-panel',
        'footer': 'footer.fixedbottom '
    },
    
    events:{
        'click #js-open-filter-panel': 'openFilterPanel'
    },
    
    initialize: function(){
        // bind custom resize event
        $(window).on("resize.nodelist", _.bind(this.adjustFooter, this));
        Nodeshot.onNodeClose = '#/nodes';
    },
    
    onClose: function () {
        // unbind custom resize event
        $(window).off("resize.nodelist");
    },
    
    onDomRefresh: function(){
        $('.selectpicker').selectpicker({
            style: 'btn-special'
        });
        
        this.adjustFooter();
    },
    
    openFilterPanel: function(e){
        var panel = this.ui.filterPanel;
        
        panel.fadeIn(25, function(){
            // clicking anywhere else closes the panel
            $('html').on('click', function(e){
                if($(e.target).parents('.filter-panel').length === 0){
                    panel.hide();
                    $('html').unbind('click')
                }
            });
        });
    },
    
    adjustFooter: function(){
        this.ui.footer.css({
            'margin-left': -1 * (($('#body').width() - $('article.center-stage').width()) / 2)
        });
    }
});
