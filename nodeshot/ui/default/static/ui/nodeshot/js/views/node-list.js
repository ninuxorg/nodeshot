(function(){
    'use strict';

    var ItemView = Marionette.ItemView.extend({
        tagName: "tr",
        template: "#node-list-row-template"
    });

    var EmptyView = Marionette.ItemView.extend({
        tagName: "tr",
        template: "#node-list-empty-template"
    });

    Ns.views.node.List = Marionette.CompositeView.extend({
        tagName: 'article',
        className: 'center-stage',
        id: 'node-list',
        template: '#node-list-template',
        childView: ItemView,
        childViewContainer: '#js-rows',
        emptyView: EmptyView,

        ui:{
            'searchInput': '#js-search input',
            'filterPanel': '#js-filter-panel',
            'footer': 'footer.fixedbottom ',
            'selects': '.selectpicker',
            'hastip': '.hastip'
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
            'sync': 'show cache'
        },

        initialize: function (options) {
            options = $.extend({
                // get main node list by default, but might also show subsets, like nodes of a user
                collection: Ns.db.nodeList || new Ns.collections.Node(),  // get cached version or init new
                addNode: true,
                partialStats: true,
                title: gettext('Node list'),
                activateMenu: true,
                cache: true
            }, options);
            this.collection = options.collection;
            this.options = options;
            // if not cached
            if (this.collection.isEmpty()) {
                // fetch from server
                this.collection.fetch();
            }
            else{
                this.show();
            }
        },

        onDestroy: function () {
            // unbind custom resize event
            $(window).off("resize.nodelist");
        },

        onDomRefresh: function(){
            this.adjustFooter();
        },

        show: function () { Ns.body.show(this) },
        cache: function() {
            if (this.options.cache) {
                Ns.db.nodeList = this.collection;
            }
        },

        onShow: function(){
            // bind custom resize event
            $(window).on("resize.nodelist", _.bind(this.adjustFooter, this));
            // tell to NodeDetailView to come back here when closing
            Ns.state.onNodeClose = this.collection.username === undefined ? 'nodes' : 'users/' + this.collection.username + '/nodes';
            // title tag
            Ns.changeTitle(this.options.title);
            if (this.options.activateMenu) {
                // mark nodes menu link as active
                Ns.menu.currentView.activate('nodes');
            }
            else {
                Ns.menu.currentView.deactivate();
            }
            // init UI elements
            this.ui.hastip.tooltip();
            this.ui.selects.selectpicker({ style: 'btn-special' });
            this.adjustFooter();
            // analytics
            Ns.track();
        },

        serializeData: function () {
            return {
                total: this.collection.count,
                collection: this.collection,
                options: this.options
            };
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
            $.createModal({ message: gettext('not implemented yet') });
        },

        search: function(e){
            e.preventDefault();
            this.collection.search(this.ui.searchInput.val()).done(function(){
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
                        $('html').unbind('click');
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
            Ns.router.navigate('map/add', { trigger: true });
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
})();
