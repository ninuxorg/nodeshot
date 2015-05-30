(function() {
    'use strict';

    Ns.views.Contact = Marionette.ItemView.extend({
        tagName: 'article',
        className: 'center-stage narrow',
        id: 'contact-container',
        template: '#form-template',

        ui: {
            'form': '#form-container',
            'errorList': '.error-list'
        },
        events: {
            'submit form': 'submit',
            'click .btn-default': 'goBack'
        },

        initialize: function (options, model) {
            if (Ns.db.user.isAuthenticated()) {
                this.model = new Ns.models.Contact(model);
                this.title = gettext('Contact') + ' ' + model.slug;
                Ns.body.show(this);
                this.successTemplate = _.template($('#contact-success-template').html());
            }
            else {
                Ns.menu.currentView.openFirst();
                delete(this);
            }
        },

        onShow: function () {
            Ns.changeTitle(this.title);
            Ns.menu.currentView.deactivate();
            Ns.track();
            this.form = new Backbone.Form({
                model: this.model,
                submitButton: gettext('Send')
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
                }).success(function(xhr){
                    self.done();
                });
            }
        },

        done: function () {
            var data = this.model.toJSON();
                data.parentFragment = this.model.parentFragment();
            this.ui.form.html(this.successTemplate(data));
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

        goBack: function () {
            Ns.router.navigate(this.model.parentFragment(), { trigger: true });
        }
    });
}());
