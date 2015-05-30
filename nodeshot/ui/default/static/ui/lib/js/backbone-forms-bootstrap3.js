/**
 * customized for nodeshot
 */
;(function(Form) {
  /**
   * Bootstrap 3 templates
   */
  Form.template = _.template('\
    <form class="form-horizontal" role="form">\
      <div data-fieldsets></div>\
      <% if (submitButton) { %>\
        <p>\
        <button type="submit" class="btn btn-success"><%= submitButton %></button>&nbsp;\
        <button type="button" class="btn btn-default">' + gettext('Cancel') + '</button>\
        </p>\
      <% } %>\
    </form>\
  ');

  Form.Fieldset.template = _.template('\
    <fieldset data-fields>\
      <% if (legend) { %>\
        <legend><%= legend %></legend>\
      <% } %>\
    </fieldset>\
  ');

  Form.Field.template = _.template('\
    <div class="form-group field-<%= key %>">\
        <label for="<%= editorId %>">\
          <% if (titleHTML){ %><%= titleHTML %>\
          <% } else { %><%- title %><% } %>\
        </label>\
        <p class="help-block hidden" data-error></p>\
        <p data-editor></p>\
        <% if(help) { %><span class="help-block"><%= help %></span><% } %>\
    </div>\
  ');

  Form.NestedField.template = _.template('\
    <div class="field-<%= key %>">\
      <div title="<% if (titleHTML){ %><%= titleHTML %><% } else { %><%- title %><% } %>" class="input-xlarge">\
        <span data-editor></span>\
        <div class="help-inline" data-error></div>\
      </div>\
      <div class="help-block"><%= help %></div>\
    </div>\
  ');

  Form.editors.Base.prototype.className = 'form-control input-sm';
  Form.Field.errorClassName = 'has-error';

  if (Form.editors.List) {
    Form.editors.List.template = _.template('\
      <div class="bbf-list">\
        <ul class="list-unstyled clearfix" data-items></ul>\
        <button type="button" class="btn bbf-add" data-action="add">Add</button>\
      </div>\
    ');

    Form.editors.List.Item.template = _.template('\
      <li class="clearfix">\
        <div class="pull-left" data-editor></div>\
        <button type="button" class="btn bbf-del" data-action="remove">&times;</button>\
      </li>\
    ');

    Form.editors.List.Object.template = Form.editors.List.NestedModel.template = _.template('\
      <div class="bbf-list-modal"><%= summary %></div>\
    ');
  }
})(Backbone.Form);
