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
const {getViewParam, getLayerName, getStyle} = require('../utils/DisasterUtils');
const layersSelectorO = state => (state.layers && state.layers.flat) || (state.layers) || (state.config && state.config.layers);
const markerSelector = state => (state.mapInfo && state.mapInfo.showMarker && state.mapInfo.clickPoint);
const geoColderSelector = state => (state.search && state.search.markerPosition);
const disasterSelector = state => ({
    riskAnalysis: state.disaster && state.disaster.riskAnalysis,
    dim: state.disaster && state.disaster.dim || {dim1: 0, dim2: 1, dim1Idx: 0, dim2Idx: 0},
    showSubUnit: state.disaster.showSubUnit,
    app: state.disaster && state.disaster.app,
    selectedEventIds: state.disaster && state.disaster.selectedEventIds || [],
    eventAnalysis: state.disaster && state.disaster.eventAnalysis || {eventAnalysis: {}}
});
// TODO currently loading flag causes a re-creation of the selector on any pan
// to avoid this separate loading from the layer object
const layersSelector = createSelector([layersSelectorO, disasterSelector],
    (layers = [], disaster) => {           
        let newLayers;
        let newFeatures;
        //const layerId = disaster.selectedEventIds.length > 0 ? '_eventAn_' : '_riskAn_';           
        const layerId = 'adminunits'
        const riskAnWMSIdx = findIndex(layers, l => l.id === layerId);        
        const riskAnLayer = layers.find(l => l.id === layerId) || false;
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
                newFeatures = adminUnitsAnLayer.features.map(f => { 
                    let value = null;  
                    if(adm_level < 1 && disaster.selectedEventIds.length == 0) {
                        const values_group_coutry = disaster.riskAnalysis.riskAnalysisData.data.event_group_country || {}
                        if(f.properties.code in values_group_coutry) {
                            value = values_group_coutry[f.properties.code]
                        }                        
                    }
                    else {                        
                        const { eventLocations, eventData } = disaster.eventAnalysis;
                        if(eventLocations) {                            
                            const match = eventData.find(e => {
                                return disaster.selectedEventIds.includes(e.entry.event.id)
                            })
                            if(match !== undefined) {
                                const location = eventLocations[f.properties.code];
                                value = location && location.occurrences || null;
                            }                                
                        }                                                
                    }
                    return {id: f.id, type: f.type, geometry: f.geometry, properties: {...f.properties, value}};
                });                              
            }   
            const riskAnWMS = assign({}, adminUnitsAnLayer, {features: newFeatures, style: newStyle});            
            newLayers = layers.slice();
            newLayers.splice(riskAnWMSIdx, 1, riskAnWMS);                     
        } else {
            newLayers = [...layers];
        }             
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
