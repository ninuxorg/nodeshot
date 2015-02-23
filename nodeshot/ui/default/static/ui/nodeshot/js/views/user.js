(function() {
    'use strict';

    Ns.views.User = Marionette.ItemView.extend({
        tagName: 'article',
        className: 'center-stage',
        id: 'user-details-container',
        template: '#user-details-template',

        events: {
            // actions
            'click .actions .icon-link': 'permalink'
        },

        modelEvents: {
            'sync': 'show cache',
            'error': 'error'
        },

        initialize: function (options) {
            // get cached version or init new
            this.model = Ns.db.users.get(options.username) || new Ns.models.User();
            // if not cached
            if (this.model.isNew()) {
                // fetch from server
                this.model.set('username', options.username).fetch();
            }
            else{
                this.show();
            }
        },

        show: function () { Ns.body.show(this); },
        cache: function () { Ns.db.users.add(this.model, { merge: true }); },
        error: function (model, http) {
            if (http.status === 404) {
                $.createModal({
                    message: gettext('the requested page was not found')
                });
            } else {
                $.createModal({
                    message: gettext('there was an error while retrieving the page')
                });
            }
        },

        onShow: function () {
            Ns.changeTitle(this.model.get('username'));
            Ns.menu.currentView.deactivate();
            Ns.track();
        },

        /**
         * prompt permalink
         */
        permalink: function (e) {
            e.preventDefault();
            var text = $(e.target).attr('data-text');
            window.prompt(text, window.location.href);
        }
    });

    Ns.views.EditUser = Ns.views.User.extend({
        template: '#form-template',

        ui: {
            'form': '#form-container',
            'errorList': '.error-list'
        },

        events: {
            'submit form': 'submit',
            'click .btn-default': 'back'
        },

        modelEvents: {},  // reset inherited modelEvents from Ns.views.User

        initialize: function (options) {
            this.model = Ns.db.user;
            this.username = this.model.get('username');
            if (!this.model.isAuthenticated()) {
                Ns.menu.currentView.openFirst();
                return;
            }
            this.show();
        },

        show: function () {
            this.title = gettext('Edit "' + this.username + '"');
            Ns.body.show(this);
            this.form = new Backbone.Form({
                model: this.model,
                submitButton: gettext('Save')
            }).render();
            this.ui.form.html(this.form.$el);
        },

        onShow: function () {
            Ns.changeTitle(this.title);
            Ns.menu.currentView.deactivate();
            Ns.track();
        },

        serializeData: function () {
            return { 'title': this.title };
        },

        submit: function (e) {
            e.preventDefault();
            // clear errors
            this.ui.form.find('.has-error').removeClass('has-error')
                        .find('.help-block').addClass('hidden');
            this.ui.errorList.html('').addClass('hidden');
            var errors = this.form.commit(),
                self = this;
            // submit if no errors
            if(!errors){
                this.model.save().fail(function(xhr){
                    self.errors(xhr);
                }).success(function(){
                    self.cache();
                    self.back();
                });
            }
        },

        /**
         * show errors
         */
        errors: function (xhr) {
            var json = xhr.responseJSON,
                form = this.ui.form,
                field;
            for (var key in json) {
                field = form.find('.field-' + key);
                if (field.length) {
                    field.addClass('has-error');
                    field.find('.help-block').text(json[key]).removeClass('hidden');
                }
                else {
                    this.ui.errorList.removeClass('hidden').append('<li>'+json[key]+'</li>');
                }
            };
        },

        back: function () {
            Ns.router.navigate('users/' + this.username, { trigger: true });
        },
    });
}());
