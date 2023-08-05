/* coding: utf-8 -*- */

/*jsl:declare Ext*/

Ext.Loader.setPath({
    MP: '/desktop/js'
});

Ext.application({
    name: 'SoL',
    appFolder: '/static/app',
    controllers: [
        'Login'
    ],

    launch: function() {
        var hash = window.location.hash;
        Ext.BLANK_IMAGE_URL = '/static/images/s.gif';
        if(hash && hash.substr(1, 15) == 'reset_password=') {
            Ext.create('SoL.window.ResetPassword', {}).show();
        } else {
            Ext.create('SoL.window.Login', {}).show();
        }
    }
});
