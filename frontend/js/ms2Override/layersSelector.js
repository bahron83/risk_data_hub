/**
* Copyright 2017, GeoSolutions Sas.
* All rights reserved.
*
* This source code is licensed under the BSD-style license found in the
* LICENSE file in the root directory of this source tree.
*/

const {createSelector} = require('reselect');
const {head, findIndex} = require('lodash');
const assign = require('object-assign');
const MapInfoUtils = require('../../MapStore2/web/client/utils/MapInfoUtils');
const LayersUtils = require('../../MapStore2/web/client/utils/LayersUtils');
const { groupEventAnalysisData } = require('../utils/DisasterUtils');
const layersSelectorO = state => (state.layers && state.layers.flat) || (state.layers) || (state.config && state.config.layers);
const markerSelector = state => (state.mapInfo && state.mapInfo.showMarker && state.mapInfo.clickPoint);
const geoColderSelector = state => (state.search && state.search.markerPosition);
const disasterSelector = state => ({
    riskAnalysis: state.disaster && state.disaster.riskAnalysis,
    dim: state.disaster && state.disaster.dim || {dim1: 0, dim2: 1, dim1Idx: 0, dim2Idx: 0},
    showSubUnit: state.disaster.showSubUnit,
    app: state.disaster && state.disaster.app,
    selectedEventIds: state.disaster && state.disaster.selectedEventIds || [],
    eventAnalysis: state.disaster && state.disaster.eventAnalysis || {eventAnalysis: {}},
    currentAdminUnits: state.disaster && state.disaster.currentAdminUnits || []
});
const { prepareEventData } = require('../selectors/disaster');
// TODO currently loading flag causes a re-creation of the selector on any pan
// to avoid this separate loading from the layer object
const layersSelector = createSelector([layersSelectorO, disasterSelector, prepareEventData],
    (layers = [], disaster, eventAnalysisData) => {           
        let newLayers;
        let newFeatures;        
        const layerId = 'adminunits';
        //console.log('layers', layers);
        const riskAnBaseIdx = findIndex(layers, l => l.id === layerId);        
        const eventLocationLayer = layers.find(l => l.id === 'event_geometry') || false;
        const adminUnitsAnLayer = layers.find(l => l.id === layerId) || false;         
        if (disaster.riskAnalysis && adminUnitsAnLayer) {  
            const dim1Value = disaster.riskAnalysis.riskAnalysisData.data.dimensions[0].values[disaster.dim.dim1Idx];
            const dim2Value = disaster.riskAnalysis.riskAnalysisData.data.dimensions[1].values[disaster.dim.dim2Idx];
            const styleIndex = disaster.riskAnalysis && parseFloat(disaster.riskAnalysis.fullContext.adm_level) + 1;
            const newStyle = disaster.riskAnalysis.riskAnalysisData.style[styleIndex];                         
            const { scope, adm_level } = disaster.riskAnalysis.fullContext;
            if(scope == 'risk') {
                newFeatures = adminUnitsAnLayer.features.map(f => { 
                    let value = null;                                    
                    for (const v of disaster.riskAnalysis.riskAnalysisData.data.subunits_values) {
                        if (v[0] == f.properties.code && v[1] == dim1Value && v[2] == dim2Value) {
                            value = v[3];                        
                            break;
                        }                        
                    }                            
                    return {id: f.id, type: f.type, geometry: f.geometry, properties: {...f.properties, value}};
                });              
                
            }
            else if(scope == 'event') {                  
                const valuesGroupAdminU = groupEventAnalysisData(eventAnalysisData, disaster.currentAdminUnits);
                //console.log('layers selector', valuesGroupAdminU, eventAnalysisData, disaster.currentAdminUnits);
                newFeatures = adminUnitsAnLayer.features.map(f => { 
                    let value = null;  
                    if(disaster.selectedEventIds.length == 0) {                                                                                                
                        const matches = valuesGroupAdminU.filter(i => i.name === f.properties.code);
                        if(matches.length > 0) {
                            value = matches[0].value;
                        }                        
                    }
                    else {                             
                        const { eventLocations, eventData } = disaster.eventAnalysis;
                        //console.log('running selector', eventLocations);
                        if(eventLocations) {                            
                            const match = eventData.find(e => {                                
                                return disaster.selectedEventIds.includes(e.entry.event.id)
                            })
                            //console.log('layer selector adm_level, feature - match', adm_level, f, match);
                            if(match !== undefined) {                                
                                const location = eventLocations[f.properties.code];                                
                                if(location !== undefined && location.level == adm_level+1)
                                    value = location && location.occurrences;                                                                                                
                            }                                
                        }                        
                    }
                    return {id: f.id, type: f.type, geometry: f.geometry, properties: {...f.properties, value}};
                });                              
            }
            
            /*let eventLocationFeatures = null;
            if(eventLocationLayer) {
                //console.log('eventLocationLayer', eventLocationLayer.features);
                eventLocationFeatures = eventLocationLayer.features.map((f, i) => {
                    //console.log('layer feature', f);
                    const id = `p${i}`;
                    return {...f, id}
                });                
            }*/
            
            const riskAnBase = assign({}, adminUnitsAnLayer, {features: newFeatures, style: newStyle});
            //const riskAnEvent = assign({}, eventLocationLayer, {features: eventLocationFeatures});
            //console.log('eventLocationLayer', riskAnEvent);
            //const howmany = eventLocationFeatures ? 2 : 1;
            //const layerList = riskAnEvent ? [riskAnBase, riskAnEvent] : [riskAnBase];
            newLayers = layers.slice();
            newLayers.splice(riskAnBaseIdx, 1, riskAnBase);                     
        } else {
            newLayers = [...layers];
        }
        //console.log('layers in selector', newLayers);
        return newLayers;
    });

const layerSelectorWithMarkers = createSelector(
    [layersSelector, markerSelector, geoColderSelector, disasterSelector],
    (layers = [], markerPosition, geocoderPosition) => {
        let newLayers = [...layers];
        if ( markerPosition ) {
            newLayers.push(MapInfoUtils.getMarkerLayer("GetFeatureInfo", markerPosition.latlng));
        }
        if (geocoderPosition) {
            newLayers.push(MapInfoUtils.getMarkerLayer("GeoCoder", geocoderPosition, "marker",
                {
                    overrideOLStyle: true,
                    style: {
                        iconUrl: "https://cdn.rawgit.com/pointhi/leaflet-color-markers/master/img/marker-icon-red.png",
                        shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/0.7.7/images/marker-shadow.png',
                        iconSize: [25, 41],
                        iconAnchor: [12, 41],
                        popupAnchor: [1, -34],
                        shadowSize: [41, 41]
                    }
                }
            ));
        }

        return newLayers;
    }
);
const disasterRiskLayerSelector = createSelector([layerSelectorWithMarkers],
    (layers) => ({
        layer: head(layers.filter((l) => l.id === "_riskAn_"))
    }));
const groupsSelector = (state) => state.layers && state.layers.flat && state.layers.groups && LayersUtils.denormalizeGroups(state.layers.flat, state.layers.groups).groups || [];

module.exports = {
    layersSelector,
    layerSelectorWithMarkers,
    groupsSelector,
    disasterRiskLayerSelector
};
