(function() {
    'use strict';

    Ns.models = {};
    Ns.collections = {};

    Ns.models.Base = Backbone.Model.extend({
        url: function () {
            var origUrl = Backbone.Model.prototype.url.call(this);
            return origUrl + (origUrl.charAt(origUrl.length - 1) === '/' ? '' : '/');
        }
    });

    Ns.models.Geo = Backbone.Model.extend({
        idAttribute: 'slug',
        leafletOptions: _.clone(Ns.settings.leafletOptions),

        initialize: function (model, options) {
            // begin temporary tweak for links
            var status = this.get('status');
            this._type = status === 'link' ? 'link' : 'node';
            // end tweak
            // set legend
            this.set('legend', Ns.db.legend.get(status));
            // update leaflet layer when geometry changes
            this.on('change:geometry', this.setLeaflet);
            // create leaflet layer
            this.setLeaflet();
        },

        /**
         * update leaflet object when changing geometry
         */
        setLeaflet: function () {
            this.set('leaflet', this.toLeaflet());
        },

        /**
         * returns leaflet object
         */
        toLeaflet: function () {
            var options = this.leafletOptions,
                legend = this.get('legend'),
                geojson,
                layer;
            // avoid exceptions if legend is unavailable
            if (legend) { legend = legend.toJSON() }
            geojson = L.geoJson(this.toGeoJSON(), {
                // set leaflet layer style
                style: function (feature) {
                    if (legend) {
                        options.fillColor = legend.fill_color;
                        options.stroke = legend.stroke_width > 0;
                        options.weight = legend.stroke_width;
                        options.color = legend.stroke_color;
                        options.className = 'marker-' + legend.slug;
                    }
                    return options;
                },
                // used only for points
                pointToLayer: function (feature, latlng) {
                    return L.circleMarker(latlng, options);
                }
            });
            // GeometryCollection objects not supported!
            layer = geojson.getLayers()[0];
            return layer;
        },

        /*
        * converts a GeoJSON object into a flat object
        */
        parse: function (geojson) {
            var obj = geojson.properties;
            obj.slug = geojson.id;
            obj.geometry = geojson.geometry;
            return obj;
        },

        /*
        * returns a GeoJSON object
        */
        toGeoJSON: function () {
            var json = this.toJSON(),
                // prepare main keys
                geojson = {
                    'type': 'Feature',
                    'id': json.slug || json.id,  // slug or id
                    'geometry': json.geometry
                };
            delete(json.geometry);
            // move rest into properties
            geojson.properties = json;
            // return geojson
            return geojson;
        }
    });

    Ns.collections.Geo = Backbone.Collection.extend({
        _url: null,
        model: Ns.models.Geo,

        /**
         * like Backbone.Collection.prototype.where but returns collection
         */
        whereCollection: function (options) {
            return new Ns.collections.Geo(this.where(options));
        },

        /**
         * allow URL to be overridden
         * load nodes.geojson by default
         */
        url: function () {
            return this._url || Ns.url('nodes.geojson');
        },

        /**
         * parse geojson
         */
        parse: function (response) {
            // temporary tweak for links
            if (this._url && this._url === Ns.url('links.geojson')) {
                _.each(response.features, function (feature) {
                    feature.properties.status = 'link';
                });
            }
            // end tweak
            return response.features;
        },

        /**
         * returns a pesudo GeoJSON object (leaflet compatible)
         */
        toGeoJSON: function () {
            return this.map(function (model) {
                return model.toGeoJSON();
            });
        }
    });

    Ns.models.Legend = Backbone.Model.extend({
        idAttribute: 'slug',
        defaults: {
            'count': '',
            'visible': true
        },

        initialize: function () {
            var hiddenGroups = localStorage.getObject('hiddenGroups', []);
            if (_.include(hiddenGroups, this.get('slug'))) {
                this.set('visible', false);
            }
            this.on('change:visible', this.storeHidden);
        },

        /**
        * remember hidden legend groups
        */
        storeHidden: function (legend, visible) {
            var hiddenGroups = localStorage.getObject('hiddenGroups', []);
            if (visible) {
                hiddenGroups = _.without(hiddenGroups, legend.id);
            }
            else {
                hiddenGroups = _.union(hiddenGroups, [legend.id]);
            }
            localStorage.setObject('hiddenGroups', hiddenGroups);
        }
    });

    Ns.collections.Legend = Backbone.Collection.extend({
        url: Ns.url('status/'),
        model: Ns.models.Legend
    });

    Ns.models.Layer = Ns.models.Base.extend({
        urlRoot: Ns.url('layers/'),
        idAttribute: 'slug',

        defaults: {
            'visible': true
        },

        initialize: function () {
            var hiddenLayers = localStorage.getObject('hiddenLayers', []);
            if (_.include(hiddenLayers, this.get('slug'))) {
                this.set('visible', false);
            }
            this.on('change:visible', this.storeHidden);
        },

        /**
         * string representation
         * used by Backbone.Forms when displaying the list of available layers
        */
        toString: function () {
            return this.get('name');
        },

        /**
        * remember hidden legend groups
        */
        storeHidden: function (layer, visible) {
            var hiddenLayers = localStorage.getObject('hiddenLayers', []);
            if (visible) {
                hiddenLayers = _.without(hiddenLayers, layer.id);
            }
            else {
                hiddenLayers = _.union(hiddenLayers, [layer.id]);
            }
            localStorage.setObject('hiddenLayers', hiddenLayers);
        }
    });

    Ns.collections.Layer = Backbone.Collection.extend({
        url: Ns.url('layers/'),
        model: Ns.models.Layer,

        /**
         * only external layers are hidden
         */
        excludeExternal: function () {
            return this.whereCollection({ is_external: false });
        },

        /**
        * external and locked (can't add new nodes) hidden
        */
        excludeExternalAndLocked: function () {
            return this.whereCollection({ is_external: false, new_nodes_allowed: true });
        },

        /**
         * like where but returns collection
         */
        whereCollection: function (options) {
            return new Ns.collections.Layer(this.where(options));
        }
    });

    Ns.models.Page = Ns.models.Base.extend({
        urlRoot: Ns.url('pages/'),
        idAttribute: 'slug'
    });

    Ns.collections.Page = Backbone.Collection.extend({
        url: Ns.url('pages/'),
        model: Ns.models.Page
    });

    Ns.models.Node = Ns.models.Base.extend({
        urlRoot: Ns.url('nodes/'),
        idAttribute: 'slug',

        schema: {
            name: { type: 'Text', title: gettext('Name'), validators: ['required'], editorAttrs: { maxlength: 75 } },
            layer: { type: 'Select', title: gettext('Layer'), validators: ['required'],
                options: function(callback){
                    // add node
                    if (typeof(Ns.body.currentView.details.currentView) === 'undefined') {
                        callback(Ns.db.layers.excludeExternalAndLocked());
                    }
                    // edit node
                    else {
                        callback(Ns.db.layers.excludeExternal());
                    }
                }
            },
            geometry: { type: 'Hidden', title: gettext('Geometry'), validators: ['required'] },
            address: { type: 'Text', title: gettext('Address'), editorAttrs: { maxlength: 150 } },
            elev: { type: 'Number', title: gettext('Elevation'),  validators: ['number'] },
            description: { type: 'TextArea', title: gettext('Description') }
        },

        defaults: {
            'relationships': false
        },

        _additionalSchema: function () {
            var self = this,
                typeMapping = {
                    'CharField': 'Text',
                    'TextField': 'TextArea',
                    'BooleanField': 'Checkbox',
                    'IntegerField': 'Number',
                    'FloatField': 'Number'
                },
                field, validators, options;
            Ns.settings.nodesHstoreSchema.forEach(function(hstoreField){
                validators = [];
                field = { title: hstoreField.label }
                field.type = typeMapping[hstoreField.class] || 'Text';
                if (hstoreField.kwargs && hstoreField.kwargs.choices) {
                    field.type = 'Select';
                    options = [];
                    hstoreField.kwargs.choices.forEach(function(choice){
                        options.push({
                            val: choice[0],
                            label: choice[1]
                        });
                    });
                    field.options = options;
                }
                if (!hstoreField.kwargs || hstoreField.kwargs.blank === false){
                    validators.push('required');
                }
                if (hstoreField.kwargs && hstoreField.kwargs.max_length){
                    field.editorAttrs = { maxlength: hstoreField.kwargs.max_length }
                }
                if (hstoreField.type === 'Number'){
                    validators.push('number');
                }
                hstoreField.validators = validators;
                self.schema[hstoreField.name] = field;
            });
        },

        initialize: function () {
            this.on('change:layer', this.setLayerName);
            this.on('change:geometry', this.setGeometry);
            this._additionalSchema();
        },

        setLayerName: function(model, value){
            this.set('layer_name', Ns.db.layers.get(value).get('name'));
        },

        setGeometry: function(model, value) {
            if (typeof value === 'string') {
                this.set('geometry', JSON.parse(value));
            }
        }
    });

    Ns.collections.Node = Backbone.PageableCollection.extend({
        model: Ns.models.Node,
        url: Ns.url('nodes/'),

        // Any `state` or `queryParam` you override in a subclass will be merged with
        // the defaults in `Backbone.PageableCollection` 's prototype.
        state: {
            pageSize: 50,
            firstPage: 1,
            currentPage: 1
        },

        queryParams: {
            currentPage: 'page',
            pageSize: 'limit',
            totalRecords: 'count'
        },

        hasNextPage: function () {
            return this.next !== null;
        },

        hasPreviousPage: function () {
            return this.previous !== null;
        },

        getNumberOfPages: function () {
            var total = this.count,
            size = this.state.pageSize;

            return Math.ceil(total / size);
        },

        search: function (q) {
            this.searchTerm = q;
            return this.getPage(1, {
                data: { search: q },
                processData: true
            });
        },

        // needed to use pagination results as the collection
        parse: function (response) {
            this.count = response.count;
            this.next = response.next;
            this.previous = response.previous;
            return response.results;
        },

        initialize: function () {
            this.searchTerm = '';
        }
    });

    /**
     * Extends Ns.collections.Node to fetch nodes of an user
     */
    Ns.collections.UserNode = Ns.collections.Node.extend({
        initialize: function (models, options) {
            this.username = options.username;
        },

        url: function () {
            return Ns.url('profiles/' + this.username + '/nodes/')
        }
    });

    Ns.models.SearchResult = Backbone.Model.extend({
        icons: {
            'node': 'pin',
            'address': 'globe'
        },

        toJSON: function () {
            var action, name, type;
            // if node
            if (typeof this.get('slug') !== 'undefined'){
                type = 'node';
                action = '#nodes/' + this.get('slug');
                name = this.get('name');
            }
            // if address
            else if (typeof this.get('lat') !== 'undefined') {
                type = 'address';
                action = '#map/latlng/' + this.get('lat') + ',' + this.get('lon');
                name = this.get('display_name');
            }
            return {
                type: type,
                action: action,
                name: name,
                icon: 'icon-' + this.icons[type]
            }
        }
    });

    Ns.collections.Search = Ns.collections.Node.extend({
        url: Ns.url('nodes/'),
        model: Ns.models.SearchResult
    });

    Ns.models.User = Ns.models.Base.extend({
        urlRoot: Ns.url('profiles/'),
        idAttribute: 'username',

        schema: {
            first_name: { type: 'Text', title: gettext('First name'), validators: ['required'], editorAttrs: { maxlength: 30 }},
            last_name: { type: 'Text', title: gettext('Last name'), validators: ['required'], editorAttrs: { maxlength: 30 }},
            city: { type: 'Text', title: gettext('City'), editorAttrs: { maxlength: 30 }},
            country: { type: 'Text', title: gettext('Country'), editorAttrs: { maxlength: 30 }},
            about: { type: 'TextArea', title: gettext('Bio') }
        },

        defaults: {
            'avatar': 'http://www.gravatar.com/avatar/default'
        },

        initialize: function () {
            this.setTruncatedUsername();
            this.on('change:username', this.setTruncatedUsername);
        },

        /*
        * truncate long usernames
        */
        setTruncatedUsername: function () {
            var username = this.get('username');
            // if username is present and longer than 15
            if (typeof (username) !== 'undefined' && username.length > 15) {
                // add an ellipsis if username is too long
                username = username.substr(0, 13) + '&hellip;';
            }
            // update model
            this.set('truncatedUsername', username);
        },

        /*
        * returns true if the user is authenticated, false otherwise
        */
        isAuthenticated: function () {
            return this.get('username') !== undefined;
        },

        /*
        * performs login
        */
        login: function (data) {
            var self = this;
            // trigger login event
            self.trigger('login');
            // Login
            $.post(Ns.url('account/login/'), data).error(function (http) {
                // TODO improve
                var json = http.responseJSON,
                errorMessage = 'Invalid username or password',
                zIndex = $('#signin-modal').css('z-index'); // original z-index
                $('#signin-modal').css('z-index', 1002); // temporarily change

                // determine correct error message to show
                errorMessage = json.non_field_errors || json.detail ||  errorMessage;

                $.createModal({
                    message: errorMessage,
                    successAction: function () {
                        $('#signin-modal').css('z-index', zIndex);
                    } // restore z-index
                });
            }).done(function (response) {
                $('#signin-modal').modal('hide');
                // load new user
                Ns.db.user.set(response.user);
                // trigger custom event
                self.trigger('loggedin');
            });
        },

        /*
        * performs logout
        */
        logout: function () {
            var self = this;
            self.clear();
            self.trigger('logout');

            $.post(Ns.url('account/logout/')).error(function () {
                // TODO: improve!
                $.createModal({ message: gettext('problem while logging out') });
            }).done(function () {
                // trigger custom event
                self.trigger('loggedout');
            });
        }
    });

    Ns.models.Notification = Ns.models.Base.extend({
        urlRoot: Ns.url('account/notifications/'),

        initialize: function () {
            this.setIcon();
        },

        /*
        * use type attribute to differentiate icons
        */
        setIcon: function () {
            var value = this.get('type').split('_')[0];
            this.set('icon', value);
        }
    });

    Ns.collections.Notification = Backbone.Collection.extend({
        model: Ns.models.Notification,
        url: Ns.url('account/notifications/?action=all&limit=15'),

        // needed to use pagination results as the collection
        parse: function (response) {
            return response.results;
        },

        /*
        * get number of unread notifications
        */
        getUnreadCount: function () {
            var count = 0;
            this.models.forEach(function (model) {
                if (model.get('is_read') === false) {
                    count += 1;
                }
            });
            return count;
        },

        /*
        * mark notifications as read
        */
        read: function () {
            // skip if all notifications are already read
            if (this.getUnreadCount() > 0) {
                $.get(this.url.split('?')[0]);
                this.models.forEach(function (model) {
                    model.set('is_read', true);
                });
                this.trigger('reset');
            }
        }
    });

    Ns.collections.Menu = Backbone.Collection.extend({
        model: Backbone.Model,
        url: Ns.url('menu/')
    });

    Ns.models.PasswordReset = Ns.models.Base.extend({
        urlRoot: Ns.url('account/password/reset/'),

        schema: {
            email: { validators: ['required', 'email'] }
        }
    });

    Ns.models.Contact = Ns.models.Base.extend({
        urlRoot: Ns.url(':type/:slug/contact/'),

        url: function () {
            var url = this.urlRoot,
                type = this.get('type'),
                slug = this.get('slug');
            if (type && slug) {
                url = url.replace(':type', type).replace(':slug', slug);
            }
            return url;
        },

        parentFragment: function () {
            var type = this.get('type'),
                type = type === 'profiles' ? 'users' : type,
                slug = this.get('slug');
            return type + '/' + slug;
        },

        schema: {
            message: { type: 'TextArea', title: gettext('Message'), validators: ['required'] }
        }
    });

    Ns.models.SocialLink = Ns.models.Base.extend({
        urlRoot: Ns.url('profiles/:user/social-links/'),

        url: function () {
            var url = this.urlRoot.replace(':user', Ns.db.user.id);
            if (!this.isNew()) {
                url = url + this.id + '/';
            }
            return url;
        },

        defaults: {
            'url': '',
            'description': ''
        },

        toJSON: function () {
            var json = Backbone.Model.prototype.toJSON.apply(this, arguments);
            json.cid = this.cid;
            return json;
        }
    });

    Ns.collections.SocialLink = Backbone.Collection.extend({
        model: Ns.models.SocialLink,
        url: function () {
            return Ns.url('profiles/' + Ns.db.user.id + '/social-links/');
        }
    });

    Ns.models.EmailAddress = Ns.models.Base.extend({
        urlRoot: Ns.url('account/email/'),

        defaults: {
            'email': '',
            'verified': false,
            'primary': false
        },

        makePrimary: function () {
            this.collection.each(function(model){
                model.set('primary', !model.get('primary'))
            })
            return this.save();
        },

        resendConfirmation: function () {
            return $.post(this.url() + 'resend-confirmation/');
        },

        toJSON: function () {
            var json = Backbone.Model.prototype.toJSON.apply(this, arguments);
            json.cid = this.cid;
            return json;
        }
    });

    Ns.collections.EmailAddress = Backbone.Collection.extend({
        model: Ns.models.EmailAddress,
        url: Ns.url('account/email/')
    });

    Ns.models.AccountPassword = Ns.models.Base.extend({
        urlRoot: Ns.url('account/password/'),
        schema: {
            current_password: { type: 'Password', title: gettext('Current password') },
            password1: { type: 'Password', title: gettext('New password'), validators: ['required'] },
            password2: { type: 'Password', title: gettext('New password (confirmation)'), validators: ['required'] }
        }
    });
}());
