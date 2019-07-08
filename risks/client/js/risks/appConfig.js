/**
 * Copyright 2016, GeoSolutions Sas.
 * All rights reserved.
 *
 * This source code is licensed under the BSD-style license found in the
 * LICENSE file in the root directory of this source tree.
 */

module.exports = {
    pages: [
    {
        name: "home",
        path: "/*",
        component: require('../pages/RisksHome')
    }],
    pluginsDef: require('./plugins.js'),
    initialState: {
        defaultState: {
            mapInfo: {
                infoFormat: "text/html"
            },
            disaster: {
                event: ''
            }
        },
        mobile: {}
    }
};