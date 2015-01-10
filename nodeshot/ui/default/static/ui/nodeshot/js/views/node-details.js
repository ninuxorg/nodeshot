(function(){
    'use strict';

    Ns.views.node.Detail = Marionette.ItemView.extend({
        tagName: 'div',
        id: 'map-overlay-container',
        template: '#node-details-template',

        ui: {
            'nodeDetails': '#node-details',
            'commentTextarea': '.new-comment textarea',
            'commentTextareaContainer': '.new-comment .form-control',
            'submitRow': '.new-comment .submit-row',
            'stars': '#js-rating a span',
            'iconThumbsUp': '.icon-thumbs-up',
            'iconThumbsDown': '.icon-thumbs-down'
        },

        events: {
            // actions
            'click .icon-link': 'permalink',
            // vote
            'click .icon-thumbs-up': 'like',
            'click .icon-thumbs-down': 'dislike',
            // comments
            'keypress @ui.commentTextarea': 'keyPressCommentTextarea',
            'keydown @ui.commentTextarea': 'keyDownCommentTextarea',
            'keyup @ui.commentTextarea': 'keyUpCommentTextarea',
            'focusout @ui.commentTextarea': 'focusOutCommentTextarea',
            'submit form.new-comment': 'submitComment',
            // rate
            'mouseover @ui.stars': 'mouseOverStar',
            'mouseout @ui.stars': 'mouseOutStar',
            'click @ui.stars': 'rate',
            // go back
            'click .icon-close': 'goBack'
        },

        modelEvents: {
            'change': 'render'
        },

        initialize: function (options) {
            this.parent = options.parent;
            this.ext = {
                legend: this.parent.legend.$el,
                toolbar: this.parent.toolbar.$el,
                map: this.parent.content.$el,
                leafletMap: this.parent.content.currentView.map,
                mapContainer: this.parent.$el,
                html: $('html'),
                body: $('body'),
                signin: $('#signin-modal')
            };
            // elements that must be hidden
            this.hidden =  $().add(this.ext.legend)
                              .add(this.ext.toolbar)
                              .add(this.ext.map.find('.leaflet-control-attribution'));
            // bind to namespaced events
            $(window).on("resize.node-details", _.bind(this.resize, this));
            this.listenTo(Ns.db.user, 'loggedin loggedout', this.render);
            // cache this model for subsequent requests
            Ns.db.nodeDetails.add(this.model);
        },

        onShow: function () {
            var map = this.ext.leafletMap,
                geomodel = new Ns.models.Geo(this.model.toJSON()),
                leaflet = geomodel.toLeaflet(),
                mapPreferences = localStorage.getObject('map') || Ns.settings.map;
            // hide elements that are not needed
            this.toggleElements();
            // fit map view to geographic object
            map.fitBounds(leaflet.getBounds(), { animate: false });
            // move map up slightly to conpensate the layout
            map.panBy([0, 90], { animate: false });
            // enable vertical scrolling
            this.ext.body.css('overflow-x', 'hidden');
            // enable tooltips
            this.$('.hastip').tooltip();
            // store coordinates in preferences
            mapPreferences.lat = leaflet.getBounds().getCenter().lat;
            mapPreferences.lng = leaflet.getBounds().getCenter().lng;
            localStorage.setObject('map', mapPreferences);
        },

        /*
         * unbind resize event when view is closed
         */
        onDestroy: function () {
            // unbind the namespaced events
            $(window).off("resize.node-details");
            // reset scrollbar styles
            this.ext.body.attr('style', '').scrollTop(0);
            // restore initial state
            this.toggleElements();
        },

        /**
         * hide/show elements that are peculiar to this view
         */
        toggleElements: function() {
            // style needed to display smaller map
            this.ext.mapContainer.toggleClass('short-map');
            // trick for uniform background color
            this.ext.html.toggleClass('details-background');
            // hide or show elements that are not needed for this view
            this.hidden.toggle();
            // resize map
            this.resize();
        },

        /*
         * resize window event
         */
        resize: function () {
            this.resizeMap();
            this.setMinHeight();
        },

        /*
         * set width and height of map
         */
        resizeMap: function(){
            Ns.views.map.Layout.resizeMap();
        },

        /*
         * layout corrections for node-details
         * set min-heigh css property on map-container div
         */
        setMinHeight: function () {
            if (this.hidden.eq(0).is(':hidden')){
                // ensure content fills until the bottom of the window
                this.ext.mapContainer.height($(window).height() - $('header').eq(0).outerHeight());

                var containerHeight = this.ext.mapContainer.outerHeight(),
                    // distance of map-overlay container from top
                    topDistance = parseInt(this.$el.css('top')),
                    newMinHeight = containerHeight - topDistance;
                // set min height if necessary
                if (newMinHeight > 150) {
                    this.ui.nodeDetails.css('min-height', newMinHeight);
                }
            }
        },

        /*
         * prompt permalink
         */
        permalink: function(e){
            e.preventDefault();
            var text = $(e.target).attr('data-text');
            window.prompt(text, window.location.href);
        },


        like: function(e) { this.vote(e, 1); },
        dislike: function(e) { this.vote(e, -1); },

        /*
         * like/dislike
         */
        vote: function(e, value){
            e.preventDefault();
            if(!Ns.db.user.isAuthenticated()){
                this.ext.signin.modal('show');
                return;
            }
            var relationships = this.model.get('relationships'),
                type = value > 0 ? 'likes' : 'dislikes',
                otherIcon = this.ui['iconThumbs' + (value > 0 ? 'Down' : 'Up')],
                backup = _.clone(relationships.counts[type]);
                self = this;
            // increment
            relationships.counts[type]++;
            this.model.set('relationships', relationships);
            $(e.target).text(relationships.counts[type]);
            otherIcon.addClass('fade');
            // post vote
            $.post(relationships.votes_url, { vote: value })
            // rollback in case of error
            .error(function(http){
                $(e.target).text(backup);
                otherIcon.removeClass('fade');
                relationships.counts[type] = backup;
                self.model.set('relationships', relationships);
                $.createModal({ message: 'error' });
            });
        },

        /* comment textarea animations */

        keyPressCommentTextarea: function(e){
            // when start entering text
            if(this.ui.commentTextarea.val().length <= 0){
                // smaller text
                this.ui.commentTextarea.removeClass('initial');
                // show submit button
                this.ui.submitRow.fadeIn(250);
                // animate height
                this.ui.commentTextareaContainer.animate({height: 100}, 250);
            }
        },

        keyDownCommentTextarea: function(e){
            // if deleting the last bit of text
            // that is: pressing backspace when only 1 character
            if(e.keyCode === 8 && this.ui.commentTextarea.val().length === 1){
                // initial textarea state
                this.ui.commentTextarea.addClass('initial');
            }
        },

        keyUpCommentTextarea: function(e){
            // if all text is deleted
            if(this.ui.commentTextarea.val().length <= 0){
                // initial textarea state
                this.ui.commentTextarea.addClass('initial');
            }
        },

        focusOutCommentTextarea: function(e){
            // if textarea empty
            if(this.ui.commentTextarea.val().length <= 0){
                // initial textarea state
                this.ui.commentTextarea.addClass('initial');
                // hide sucmit button
                this.ui.submitRow.fadeOut(250);
                // reset height
                this.ui.commentTextareaContainer.animate({height: 50}, 250);
            }
        },

        /*
         * add comment
         */
        submitComment: function(e){
            e.preventDefault();
            var self = this,
                relationships = this.model.get('relationships'),
                commentText = this.ui.commentTextarea.val(),
                comments;
            // add comment to UI
            relationships.comments.push(
                {
                    "user": Ns.db.user.toJSON(),
                    "text": commentText,
                    "added": Date.now()
                }
            );
            this.model.set('relationships', relationships);
            this.model.trigger('change');
            comments = this.$('.comment')
            // scroll to last comment
            if(comments.length){
                $('html, body').animate({
                    scrollTop: comments.last().offset().top
                }, 100);
            }
            // add comment to DB
            $.post(relationships.comments_url, { text: commentText })
            // rollback in case of error
            .error(function(){
                // remove last comment
                relationships.comments.pop();
                self.model.set('relationships', relationships);
                self.model.trigger('change');
                // display error
                $.createModal({ message: 'error' });
            });
        },

        /*
         * highlight stars on mouse over
         */
        mouseOverStar: function(e){
            var target = $(e.target),
                currentNumber = target.attr('data-number');

            _.each(this.ui.stars, function(el, i){
                if(currentNumber >= i){
                    $(el).attr('class', 'icon-star-full');
                }
            });
        },

        /*
         * restore stars original status on mouseout
         */
        mouseOutStar: function(e){
            _.each(this.ui.stars, function(el, i){
                $(el).attr('class', $(el).attr('data-original-class'));
            });
        },

        /*
         * submit rating, only if logged in
         */
        rate: function(e){
            e.preventDefault();
            if(!Ns.db.user.isAuthenticated()){
                this.ext.signin.modal('show');
                return;
            }
            var relationships = this.model.get('relationships'),
                value = (parseInt($(e.target).attr('data-number')) + 1) * 2,  // (0-index value + 1) * 2
                self = this;
            $.post(relationships.ratings_url, { "value": value })
            .done(function(){
                $.createModal({ message: self.$('#js-rating').attr('data-thanks-message') });
                self.model.fetch();
            })
            .error(function(xhr){
                $.createModal({ message: xhr.responseJSON["__all__"] });
            });
        },

        /*
         * go back (to map or node list)
         */
        goBack: function(e){
            e.preventDefault();
            Ns.router.navigate(
                Ns.state.onNodeClose,
                { trigger: true }
            )
        }
    });
})();
