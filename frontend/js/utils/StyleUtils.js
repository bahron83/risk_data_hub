/*
 * Copyright 2018, GeoSolutions Sas.
 * All rights reserved.
 *
 * This source code is licensed under the BSD-style license found in the
 * LICENSE file in the root directory of this source tree.
 */

module.exports = {     
    getMainViewStyle: () => ({
        color: 'black',
        fillColor: 'transparent',
        weight: 1,
        opacity: 1,
        fillOpacity: 0
    }),
    getRiskAnStyle: rangeValues => ({
        color: 'black',
        fillColor: 'transparent',
        weight: 1,
        opacity: 1,
        fillOpacity: 1,
        rules: rangeValues
    }),
    getSearchLayerStyle: () => ({
        iconUrl: "/static/dataexplorationtool/img/marker.svg",
        shadowUrl: "/static/dataexplorationtool/img/marker-shadow.png",
        iconSize: [
            25,
            41
        ],
        iconAnchor: [
            12,
            41
        ],
        popupAnchor: [
            1,
            -34
        ],
        shadowSize: [
            41,
            41
        ],
        stroke: {
            color: "#555",
            width: 2,
            opacity: 1,
            lineDash: [
                4,
                6
            ]
        },
        fill: {
            color: "rgba(18, 18, 18, 0.1)"
        }
    }),
    getBBOXStyle: () => ({
        strokeColor: '#21bab0',
        strokeWidth: 5,
        fillColor: [255, 255, 255, 0.1]
    })
};