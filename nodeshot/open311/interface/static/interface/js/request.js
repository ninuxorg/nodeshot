var request = getData(window.__BASEURL__ + 'api/v1/open311/requests/' + request_id); //layers
console.log(request)
var tmplMarkup = $('#tmplOpen311Request').html();
        var compiledTmpl = _.template(tmplMarkup, {
            request: request
        });
        $("#request").append(compiledTmpl);