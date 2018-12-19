/**
 * Copyright 2016, GeoSolutions Sas.
 * All rights reserved.
 *
 * This source code is licensed under the BSD-style license found in the
 * LICENSE file in the root directory of this source tree.
 */

//data from Home Page
const disasterRisk = JSON.parse(localStorage.getItem("disasterRisk"));
const defaultUrlPrefix = '';
const contextUrlPrefix = disasterRisk && disasterRisk.contextUrl || defaultUrlPrefix;

module.exports = {
    pages: [{
        name: "home",
        path: "/",
        component: require('./pages/Home')
    }, {
        name: "main",
        path: "/main",
        component: require('./pages/Main')
    }],
    themeCfg: {
        path: `${contextUrlPrefix}/static/js`
    },
    initialState: {
        defaultState: {
            //mousePosition: {enabled: false},
            controls: {
                help: {
                    enabled: false
                },
                details: {
                    enabled: false
                },
                print: {
                    enabled: false
                },
                toolbar: {
                    active: null,
                    expanded: false
                },
                drawer: {
                    enabled: false,
                    menu: "1"
                },
                RefreshLayers: {
                    enabled: false,
                    options: {
                        bbox: true,
                        search: true,
                        title: false,
                        dimensions: false
                    }
                },
                cookie: {
                    enabled: false,
                    seeMore: false
                }
            },
            disaster: {
                app: 'risks',
                contextUrl: contextUrlPrefix,
                disasterRisk: disasterRisk
            }
        },        
        mobile: {
            mapInfo: {enabled: true, infoFormat: 'application/json' },
            //mousePosition: {enabled: true, crs: "EPSG:4326", showCenter: true}
        }
    },
    appEpics: {},
    storeOpts: {
        persist: {
            whitelist: ['security']
        }
    }
};