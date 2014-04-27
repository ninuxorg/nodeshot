var NodeDetailsView = Backbone.Marionette.ItemView.extend({
    name: 'NodeDetailsView',
    tagName: 'div',
    id: 'map-container',
    className: 'short-map',
    template: '#node-details-template',
    
    ui: {
        'commentTextarea': '.new-comment textarea',
        'commentTextareaContainer': '.new-comment .form-control',
        'submitRow': '.new-comment .submit-row'
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
        'submit form.new-comment': 'submitComment'
    },
    
    modelEvents: {
        'change': 'render'
    },

    onDomRefresh: function () {
        var slug = this.model.get('slug'),
            marker = Nodeshot.nodesNamed[slug],
            // init map on node coordinates and with high zoom (17)
            map = L.map('map-js', {
                trackResize: true,
                scrollWheelZoom: false
            }).setView(marker._latlng, 17);
        
        // TODO: FIXME & DRY
        marker = L.circleMarker(marker._latlng, marker.options);
        // add marker to map
        map.addLayer(marker);
        // move map up slightly
        map.panBy([0, 90], {
            animate: false
        });
        // TODO: configurable tiles
        // TODO: rename mapbox in osm
        this.mapBoxLayer = new L.tileLayer('//a.tiles.mapbox.com/v3/nemesisdesign.hcj0ha2h/{z}/{x}/{y}.png').addTo(map);
        this.map = map;

        $('body').attr('style', '').css({
            'overflow-x': 'hidden',
            'overflow-y': 'auto'
        });
        setMapDimensions();
        this.setMinHeight();
    },

    initialize: function () {
        // bind to namespaced events
        $(window).on("resize.node-details", _.bind(this.resize, this));
        
        // fetch details from DB
        this.model.fetch();
        
        this.listenTo(Nodeshot.currentUser, 'change', function(){ this.render() });
    },

    /*
     * unbind resize event when view is closed
     */
    onClose: function () {
        // unbind the namespaced events
        $(window).off("resize.node-details");
    },

    /*
     * resize window event
     */
    resize: function () {
        setMapDimensions();
        this.setMinHeight();
    },
    
    /*
     * set min-heigh css property on map-container div
     */
    setMinHeight: function () {
        var containerHeight = $('#map-container').outerHeight(),
            topDistance = parseInt($('#map-overlay-container').css('top').replace('px', ''));
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
        window.prompt(text, window.location.href)
    },
    
    /*
     * like
     */
    like: function(e){
        e.preventDefault();
        
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
            createModal({ message: 'error' })
        });
    },
    
    /*
     * dislike
     */
    dislike: function(e){
        e.preventDefault();
        
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
            createModal({ message: 'error' })
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
                "user": Nodeshot.currentUser.toJSON(),
                "text": commentText,
                "added": Date.now()
            }
        )
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
            createModal({ message: 'error' });
        });
    }
});
