getParticipationData()
var request = getData(window.__BASEURL__ + 'api/v1/open311/requests/' + request_id); //layers
var tmplMarkup = $('#tmplOpen311Request').html();
        var compiledTmpl = _.template(tmplMarkup, {
            request: request
        });
        $("#request").append(compiledTmpl);

//Votes
if (nodeSettings.participation_settings.voting_allowed) {
    //console.log("Votes OK")
    showVotes(nodeParticipation.participation.likes,nodeParticipation.participation.dislikes)
}

//Comments       
if (nodeSettings.participation_settings.comments_allowed) {
    //console.log("Comments OK")
    showComments(nodeSlug,nodeParticipation.participation.comment_count); 
}

//Comments       
if (nodeSettings.participation_settings.rating_allowed) {
    //console.log("Rating OK")
    showRating(nodeSlug,nodeParticipation.participation.rating_avg,nodeParticipation.participation.rating_count); 
}

