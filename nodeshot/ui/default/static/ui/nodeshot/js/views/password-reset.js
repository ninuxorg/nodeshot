(function() {
    'use strict';

    Ns.views.PasswordReset = Marionette.ItemView.extend({
        tagName: 'article',
        className: 'center-stage narrow',
        id: 'password-reset-container',
        template: '#form-template',

        ui: {
            'form': '#form-container',
            'errorList': '.error-list'
        },
        events: {
            'submit form': 'submit',
            'click .btn-default': 'goHome'
        },
        modelEvents: {
            'sync': 'done'
        },

        initialize: function (options) {
            if (Ns.db.user.isAuthenticated() === false) {
                this.model = new Ns.models.PasswordReset();
                this.title = gettext('Reset Password');
                // hide signin
                $('#signin-modal').modal('hide');
                Ns.body.show(this);
                this.listenTo(Ns.db.user, 'loggedin', this.goHome);
            }
            else {
                Ns.menu.currentView.openFirst();
                delete this;
            }
        },

        onShow: function () {
            Ns.changeTitle(this.title);
            Ns.menu.currentView.deactivate();
            Ns.track();
            this.form = new Backbone.Form({
                model: this.model,
                submitButton: gettext('Reset Password')
            }).render();
            this.ui.form.html(this.form.$el);
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
                });
            }
        },

        done: function () {
            this.ui.form.html(gettext('Check your inbox for the password reset link.'));
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

        goHome: function () {
            Ns.menu.currentView.openFirst();
        }
    });
}());
