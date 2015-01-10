(function(){
    'use strict';

    Ns.views.node.Detail = Marionette.ItemView.extend({
        name: 'Ns.views.node.Detail',
        tagName: 'div',
        id: 'map-container',
        className: 'short-map',
        template: '#node-details-template',

        ui: {
            'commentTextarea': '.new-comment textarea',
            'commentTextareaContainer': '.new-comment .form-control',
            'submitRow': '.new-comment .submit-row',
            'stars': '#js-rating a span'
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

        initialize: function () {
            // bind to namespaced events
            $(window).on("resize.node-details", _.bind(this.resize, this));
            this.listenTo(Ns.db.user, 'loggedin loggedout', this.render);
            // trick for background color
            $('html').css('background-color', '#aba49c');
        },

        onShow: function () {
            var map = $.loadDjangoLeafletMap(),
                geomodel = new Ns.models.Geo(this.model.toJSON()),
                leaflet = geomodel.toLeaflet(),
                mapPreferences = localStorage.getObject('map') || Ns.settings.map;

            map.fitBounds(leaflet.getBounds());
            // add leaflet layer to map
            map.addLayer(leaflet);
            // move map up slightly
            map.panBy([0, 90], {
                animate: false
            });
            // this.osmLayer = new L.tileLayer(Ns.TILESERVER_URL).addTo(map);
            this.map = map;

            $('body').attr('style', '').css({
                'overflow-x': 'hidden',
                'overflow-y': 'auto'
            });
            this.resizeMap();
            this.setMinHeight();

            // enable tooltips
            $('.hastip').tooltip();

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
            // restore background color
            $('html').attr('style', '');
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
            // ensure content fills until the bottom of the window
            $('#map-container').height($(window).height() - $('header').eq(0).outerHeight());

            var containerHeight = $('#map-container').outerHeight(),
                // distance of map-overlay container from top
                topDistance = parseInt($('#map-overlay-container').css('top')),
                newMinHeight = containerHeight - topDistance;

            if (newMinHeight > 150) {
                $('#node-details').css('min-height', newMinHeight);
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

        /*
         * like
         */
        like: function(e){
            e.preventDefault();
            if(!Ns.db.user.isAuthenticated()){
                $('#signin-modal').modal('show');
                return;
            }

            var relationships = this.model.get('relationships'),
                backup = relationships.counts.likes,
                self = this;
            // increment
            relationships.counts.likes++;
            this.model.set('relationships', relationships);
            $(e.target).text(relationships.counts.likes);
            $('.icon-thumbs-down').addClass('fade');

            $.post(relationships.votes_url, { vote: 1 })
            // restore backup in case of error
            .error(function(http){
                $(e.target).text(backup);
                $('.icon-thumbs-down').removeClass('fade');
                relationships.counts.likes = backup;
                self.model.set('relationships', relationships);
                $.createModal({ message: 'error' });
            });
        },

        /*
         * dislike
         */
        dislike: function(e){
            e.preventDefault();
            if(!Ns.db.user.isAuthenticated()){
                $('#signin-modal').modal('show');
                return;
            }

            var relationships = this.model.get('relationships'),
                backup = relationships.counts.dislikes,
                self = this;
            // increment
            relationships.counts.dislikes++;
            this.model.set('relationships', relationships);
            $(e.target).text(relationships.counts.dislikes);
            $('.icon-thumbs-up').addClass('fade');

            $.post(relationships.votes_url, { vote: -1 })
            // rollback in case of error
            .error(function(http){
                $(e.target).text(backup);
                $('.icon-thumbs-down').removeClass('fade');
                relationships.counts.dislikes = backup;
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
                commentText = this.ui.commentTextarea.val();

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
            // scroll to last comment
            if($('.comment').length){
                $('html, body').animate({
                    scrollTop: $('.comment').last().offset().top
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
                $('#signin-modal').modal('show');
                return;
            }

            var relationships = this.model.get('relationships'),
                value = (parseInt($(e.target).attr('data-number')) + 1) * 2,  // (0-index value + 1) * 2
                self = this;

            $.post(relationships.ratings_url, { "value": value })
            .done(function(){
                $.createModal({ message: $('#js-rating').attr('data-thanks-message') });
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
