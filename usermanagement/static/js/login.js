window.fbAsyncInit = function() {
    FB.init({
        appId: '104056044837930', // App ID
        channelURL: '', // Channel File, not required so leave empty
        status: true, // check login status
        cookie: true, // enable cookies to allow the server to access the session
        oauth: true, // enable OAuth 2.0
        xfbml: false // parse XFBML
    });
};

// logs the user in the application and facebook
function login() {
    FB.getLoginStatus(function(r) {
        if (r.status === 'connected') {
            window.location.href = 'fbconnect.php';
        } else {
            FB.login(function(response) {
                if (response.authResponse) {
                    //if (response.perms)
                    window.location.href = 'fbconnect.php';
                } else {
                    // user is not logged in
                }
            }, { scope: 'email' }); // which data to access from user profile
        }
    });
}

// Load the SDK Asynchronously
(function() {
    var e = document.createElement('script');
    e.async = true;
    e.src = document.location.protocol + '//connect.facebook.net/en_US/all.js';
    document.getElementById('fb-root').appendChild(e);
}());