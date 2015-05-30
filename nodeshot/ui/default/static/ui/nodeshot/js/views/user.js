(function() {
    'use strict';

    Ns.views.User = Marionette.ItemView.extend({
        tagName: 'article',
        className: 'center-stage',
        id: 'user-details-container',
        template: '#user-details-template',

        events: {
            // actions
            'click .actions .icon-link': 'permalink',
            'click .icon-mail': 'contact'
        },

        modelEvents: {
            'sync': 'show cache',
            'error': 'error'
        },

        initialize: function (options) {
            // listen to logout events
            this.listenTo(Ns.db.user, 'loggedin loggedout', this.render);
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
        },

        contact: function (e) {
            if(!Ns.db.user.isAuthenticated()){
                e.preventDefault();
                $('#signin-modal').modal('show');
                return;
            }
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
                delete(this);
                return;
            }
            // delete view on logout
            this.listenTo(Ns.db.user, 'loggedout', this.initialize);
            this.title = gettext('Edit "' + this.username + '"');
            this.show();
        },

        show: function () {
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
            Ns.router.navigate('account', { trigger: true });
        },
    });

    Ns.views.Account = Marionette.ItemView.extend({
        tagName: 'article',
        className: 'center-stage',
        id: 'account-container',
        template: '#account-template',

        ui: {
            'links': '#js-links',
            'emails': '#js-emails'
        },

        events: {
            'keydown form input': 'keydownOnInput',
            'click #js-links .add': 'addLink',
            'click #js-links .edit': 'editLink',
            'submit #js-links form': 'saveLink',
            'click #js-links .cancel': 'cancelSaveLink',
            'click #js-links .delete': 'deleteLink',
            'click #js-emails .add': 'addEmail',
            'submit #js-emails form': 'saveEmail',
            'click #js-emails .cancel': 'cancelSaveEmail',
            'click #js-emails .delete': 'deleteEmail',
            'click #js-emails .makeprimary': 'makePrimary',
            'click #js-emails .resend': 'resendConfirmation'
        },

        initialize: function (options) {
            this.model = Ns.db.user;
            if (!this.model.isAuthenticated()) {
                Ns.menu.currentView.openFirst();
                delete(this);
                return;
            }
            // delete view on logout
            this.listenTo(Ns.db.user, 'loggedout', this.initialize);
            // social links
            this.socialLinks = new Ns.collections.SocialLink(this.model.get('social_links'));
            this.model.set('social_links', this.socialLinks.toJSON());
            this.listenTo(this.socialLinks, 'add remove sync', this.updateLinks);
            this.listenTo(this.socialLinks, 'sync', this.cache);
            this.editLinkTemplate = _.template($('#edit-link-template').html());
            // email addresses
            this.emailAddresses = new Ns.collections.EmailAddress(this.model.get('email_addresses'));
            this.model.set('email_addresses', this.emailAddresses.toJSON());
            this.listenTo(this.emailAddresses, 'add remove sync', this.updateEmails);
            this.editEmailTemplate = _.template($('#edit-email-template').html());
            this.show();
        },

        show: function () { Ns.body.show(this); },

        onShow: function () {
            Ns.changeTitle(gettext('Account'));
            Ns.menu.currentView.deactivate();
            Ns.track();
        },

        updateLinks: function () {
            this.model.set('social_links', this.socialLinks.toJSON());
            this.render();
        },

        cache: function () {
            Ns.db.users.add(this.model, { merge: true });
        },

        addLink: function (e) {
            // add one at time
            if (this.socialLinks.length === 0 || !this.socialLinks.last().isNew()) {
                this.socialLinks.add(new Ns.models.SocialLink());
                this.ui.links.find('tr').last().find('.edit').trigger('click');
            }
        },

        editLink: function (e, link) {
            var cid = $(e.target).attr('data-cid'),
                tr = $(e.target).parents('tr');
            link = this.socialLinks.get(cid) || this.socialLinks.last();
            tr.html(this.editLinkTemplate(link.toJSON()));
        },

        saveLink: function (e) {
            e.preventDefault();
            var form = $(e.target),
                cid = form.find('button.cancel').attr('data-cid'),
                link = this.socialLinks.get(cid);
            link.set(form.serializeJSON());
            link.save().fail(function(xhr){
                $.createModal({ message: xhr.responseJSON.__all__.join(', ') });
            });
        },

        keydownOnInput: function (e) {
            if (e.keyCode === 27) {
                $(e.target).parents('tr').find('.cancel').trigger('click');
            }
        },

        cancelSaveLink: function (e) {
            var cid = $(e.target).attr('data-cid'),
                link = this.socialLinks.get(cid);
            if (link.isNew()) {
                link.destroy();
            }
            else {
                this.render();
            }
        },

        deleteLink: function (e) {
            var cid = $(e.target).attr('data-cid'),
                link = this.socialLinks.get(cid);
            $.createModal({
                message: gettext('Do you confirm?'),
                successMessage: gettext('yes'),
                successAction: function(){
                    link.destroy();
                },
                defaultMessage: gettext('no'),
            });
        },

        updateEmails: function () {
            this.model.set('email_addresses', this.emailAddresses.toJSON());
            this.render();
        },

        addEmail: function (e) {
            // add one at time
            if (this.emailAddresses.length === 0 || !this.emailAddresses.last().isNew()) {
                var emailAddress = new Ns.models.EmailAddress(),
                    html = this.editEmailTemplate(emailAddress.toJSON());
                this.emailAddresses.add(emailAddress);
                this.ui.emails.find('tr').last().html(html);
            }
        },

        cancelSaveEmail: function (e) {
            var cid = $(e.target).attr('data-cid'),
                email = this.emailAddresses.get(cid);
            if (email.isNew()) {
                email.destroy();
            }
            else {
                this.render();
            }
        },

        saveEmail: function (e) {
            e.preventDefault();
            var form = $(e.target),
                cid = form.find('button.cancel').attr('data-cid'),
                email = this.emailAddresses.get(cid);
            email.set(form.serializeJSON());
            email.save().fail(function(xhr){
                $.createModal({ message: xhr.responseJSON.__all__.join(', ') });
            });
        },

        deleteEmail: function (e) {
            var cid = $(e.target).attr('data-cid'),
                email = this.emailAddresses.get(cid);
            $.createModal({
                message: gettext('Do you confirm?'),
                successMessage: gettext('yes'),
                successAction: function(){
                    email.destroy();
                },
                defaultMessage: gettext('no'),
            });
        },

        makePrimary: function (e) {
            var cid = $(e.target).attr('data-cid'),
                email = this.emailAddresses.get(cid);
            email.makePrimary();
        },

        resendConfirmation: function (e) {
            var cid = $(e.target).attr('data-cid'),
                email = this.emailAddresses.get(cid);
            email.resendConfirmation().done(function(responseJSON){
                $.createModal({ message: responseJSON.detail });
            });
        }
    });

    Ns.views.AccountPassword = Ns.views.EditUser.extend({
        id: 'account-container',
        template: '#form-template',

        initialize: function (options) {
            this.model = new Ns.models.AccountPassword();
            if (!Ns.db.user.isAuthenticated()) {
                Ns.menu.currentView.openFirst();
                delete(this);
                return;
            }
            // delete view on logout
            this.listenTo(Ns.db.user, 'loggedout', this.initialize);
            this.title = gettext('Change account password');
            this.show();
        }
    });
}());
