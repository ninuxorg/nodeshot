(function(){
    var connect = function(){
        var socket,
        url,
        querystring = '';

        if(Ns.db.user.isAuthenticated()){
            querystring = '?user_id='+Ns.db.user.get('id');
        }

        url = "ws://"+ __websockets__.DOMAIN + __websockets__.PATH + ":" + __websockets__.PORT + "/" + querystring;

        try {
            var socket = new WebSocket(url);

            socket.onmessage = function(msg) {
                try{
                    data = JSON.parse(msg.data);
                    // if we got a notification update the UI
                    if(data.model == 'notification'){
                        Ns.notifications.currentView.collection.fetch({ reset: true })
                    }
                }
                catch(e){
                    if(typeof(console) !== undefined){
                        console.log(msg.data);
                    }
                }
            }

            __websockets__.socket = socket;
        } catch (e) {
            if(typeof(console) !== undefined){
                console.log('could not connect to websocket server');
            }
        }
    },
    user = Ns.db.user;

    user.on('change:username', function(){
        // close any previous connection if present
        if(__websockets__.socket){
            __websockets__.socket.close();
        }
        // connect only if authenticated
        if(user.isAuthenticated()){
            connect();
        }
    });

    if(user.isAuthenticated()){
        connect();
    }
})();
