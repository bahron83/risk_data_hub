/**
 * Copyright 2017, GeoSolutions Sas.
 * All rights reserved.
 *
 * This source code is licensed under the BSD-style license found in the
 * LICENSE file in the root directory of this source tree.
 */
const Rx = require('rxjs');
const Api = require('../api/riskdata');
const {zoomToExtent} = require('../../MapStore2/web/client/actions/map');
const {setupTutorial} = require('../../MapStore2/web/client/actions/tutorial');
const {info, error} = require('react-notification-system-redux');
const bbox = require('turf-bbox');
const {changeLayerProperties, addLayer, removeNode, removeLayer, toggleNode} = require('../../MapStore2/web/client/actions/layers');
const assign = require('object-assign');
const {find} = require('lodash');
const _ = require('lodash');
const {configLayer, configRefLayer, getStyleRef, makeNotificationBody, getLayerTitle, getLayerTitleEvents} = require('../utils/DisasterUtils');
const ConfigUtils = require('../../MapStore2/web/client/utils/ConfigUtils');

const {
    GET_DATA,
    LOAD_RISK_MAP_CONFIG,
    GET_RISK_FEATURES,
    GET_ANALYSIS_DATA,
    GET_EVENT_DATA,    
    SELECT_EVENT,
    EVENT_DETAILS,  
    INIT_RISK_APP,
    DATA_LOADED,
    ANALYSIS_DATA_LOADED,
    EVENT_DATA_LOADED,
    DATA_ERROR,
    DATA_LOADING,
    GET_S_FURTHER_RESOURCE_DATA,
    CHART_SLIDER_UPDATE,
    SET_FILTERS,
    ADM_LOOKUP,
    SWITCH_CONTEXT,
    dataLoaded,
    dataLoading,
    dataError,
    featuresLoaded,
    featuresLoading,
    featuresError,
    getFeatures,
    getAnalysisData,
    getEventData,
    analysisDataLoaded,
    eventDataLoaded,
    eventDetailsLoaded,
    getData,
    setChartSliderIndex,
    zoomInOut,
    admLookupLoaded,
    eventDetails     
} = require('../actions/disaster');
const {configureMap, configureError} = require('../../MapStore2/web/client/actions/config');
const getRiskDataEpic = (action$, store) =>
    action$.ofType(GET_DATA).switchMap(action =>
        Rx.Observable.defer(() => Api.getData(action.url))
        .retry(1).
        map((data) => {
            const layers = (store.getState()).layers;
            const hasGis = find(layers.groups, g => g.id === 'Gis Overlays');
            const hasRiskAn = find(layers.flat, l => l.id === '_riskAn_');
            return [ hasGis && removeNode("Gis Overlays", "groups"), hasRiskAn && removeNode("_riskAn_", "layers"), dataLoaded(data, action.cleanState)].filter(a => a);
        })
        .mergeAll()
        .startWith(dataLoading(true))
            .catch(e => Rx.Observable.of(dataError(e)))
    );
const getRiskMapConfig = action$ =>
    action$.ofType(LOAD_RISK_MAP_CONFIG).switchMap(action =>
            Rx.Observable.fromPromise(Api.getData(action.configName))
                .map(val => [configureMap(val), getFeatures(action.featuresUrl)])
                .mergeAll()
                .catch(e => Rx.Observable.of(configureError(e)))
        );
const getRiskFeatures = (action$, store) =>
    action$.ofType(GET_RISK_FEATURES)
    .audit(() => {
        const isMapConfigured = (store.getState()).mapInitialConfig && true;
        return isMapConfigured && Rx.Observable.of(isMapConfigured) || action$.ofType('MAP_CONFIG_LOADED');
    })
    .switchMap(action =>
        Rx.Observable.defer(() => Api.getData(action.url))
        .retry(1)
        .map(val => [zoomToExtent(bbox(val.features[0]), "EPSG:4326"),
                changeLayerProperties("adminunits", {features: val.features.map((f, idx) => (assign({}, f, {id: idx}))) || []}),
                featuresLoaded(val.features)])
        .mergeAll()
        .startWith(featuresLoading())
        .catch(e => Rx.Observable.of(featuresError(e)))
    );
const getAnalysisEpic = (action$, store) =>
    action$.ofType(GET_ANALYSIS_DATA).switchMap(action => {  
        const { analysisFilters } = (store.getState()).disaster; 
        //console.log(analysisFilters);
        let filtersString = '';
        _.forIn(analysisFilters, (value, key) => { if(value != '') filtersString += `${key}/${value}/` });
        const apiUrl = action.url + filtersString;
        return Rx.Observable.defer(() => Api.getData(apiUrl))
            .retry(1)
            .map(val => {
                const baseUrl = val.wms && val.wms.baseurl;
                const anLayers = val.riskAnalysisData && val.riskAnalysisData.additionalLayers || [];
                const referenceLayer = val.riskAnalysisData && val.riskAnalysisData.referenceLayer;
                const layers = (store.getState()).layers;                
                const {app, dim} = (store.getState()).disaster;                                 
                
                //additional gis layers
                let anLayerDim = [];
                //check for layers on X and Y axis                
                const dimX = dim && dim.dim1 == 0 ? "dim1Idx" : "dim2Idx";
                const dimY = dim && dim.dim1 == 0 ? "dim2Idx" : "dim1Idx";
                for(var i=0;i<2;i++) {                    
                    const dimIdx = i == 0 ? dimX : dimY;
                    const indexOfAdditionalLayer = (dim == {} || dim === undefined) ? 0 : dim[dimIdx];
                    const dimensions = val.riskAnalysisData.data.dimensions;
                    const valueOfAdditionalLayer = dimensions[i].values[indexOfAdditionalLayer];
                    const resource = dimensions[i]['layers'][valueOfAdditionalLayer]['resource'];
                    const layerDetails = resource != null ? resource['details'] : null;
                    let layerName = "";                    
                    if(layerDetails != null) {
                        const parts = layerDetails.split("/");
                        layerName = parts[parts.length - 1];
                    }
                    anLayers.map((arr, index) => { if(arr[1] == layerName) anLayerDim.push(arr) });                
                }
                
                const hasGis = find(layers.groups, g => g.id === 'Gis Overlays');
                const hasAnalysisLayer = find(layers.flat, l => l.id === '_riskAn_');                                                
                //data adjustment for event grouped_values
                let adjustedVal = val;                
                if(val.riskAnalysisData.data.grouped_values !== undefined) {
                    if(val.riskAnalysisData.data.grouped_values.length == 0) {
                        const {riskAnalysis} = (store.getState()).disaster;
                        adjustedVal.riskAnalysisData.data.grouped_values = riskAnalysis.riskAnalysisData.data.grouped_values
                    }
                }
                
                const actions = [                    
                    analysisDataLoaded(adjustedVal),
                    hasGis && removeNode("Gis Overlays", "groups"),
                    !hasAnalysisLayer && addLayer(configLayer(baseUrl, "", '_riskAn_', getLayerTitle({riskAnalysis: val, app}), true, "Default"), false),
                    app !== 'costs' && referenceLayer && referenceLayer.layerName && referenceLayer.layerTitle && addLayer(configRefLayer(baseUrl, referenceLayer.layerName, "_refLayer_", referenceLayer.layerTitle, getStyleRef(val), true, "Gis Overlays"), false)
                ].concat(anLayerDim.map((l) => addLayer(configLayer(baseUrl, l[1], `ral_${l[0]}`, l[2] || l[1].split(':').pop(), true, 'Gis Overlays')))).filter(a => a);

                return actions;
            })
            .mergeAll()
            .startWith(dataLoading(true))                        
            .catch( e => Rx.Observable.of(info({title: "Info", message: e.data && e.data.errors || "Error while loading data...", position: 'tc', autoDismiss: 3})))
        });
const getEventEpic = (action$, store) =>
    action$.ofType(GET_EVENT_DATA).switchMap(action => 
        Rx.Observable.defer(() => Api.getData(action.url))
            .retry(1)
            .map(val => {
                const baseUrl = val.wms && val.wms.baseurl;
                const anLayers = val.relatedLayers || [];                
                const layers = (store.getState()).layers;
                const {app} = (store.getState()).disaster;                
                const hasGis = find(layers.groups, g => g.id === 'Gis Overlays');
                const hasEventLayer = find(layers.flat, l => l.id === '_eventAn_');                                                
                const actions = [                                        
                    eventDataLoaded(val),
                    hasGis && removeNode("Gis Overlays", "groups"),
                    !hasEventLayer && addLayer(configLayer(baseUrl, "", '_eventAn_', getLayerTitleEvents({eventAnalysis: val, app}), true, "Default"), false)                    
                ].concat(anLayers.map((l) => addLayer(configLayer(baseUrl, l[1], `ral_${l[0]}`, l[2] || l[1].split(':').pop(), true, 'Gis Overlays')))).filter(a => a);

                return actions;
            })
            .mergeAll()
            .startWith(dataLoading(true))            
            .catch(e => Rx.Observable.of(dataError(e)))
    );

const getEventDetailsEpic = (action$, store) =>
    action$.ofType(EVENT_DETAILS).switchMap(action => 
        Rx.Observable.defer(() => Api.getData(action.url))
            .retry(1)
            .map(val => {
                return [eventDetailsLoaded(val)];
            })
            .mergeAll()
            .startWith(dataLoading(true))            
            .catch(e => Rx.Observable.of(dataError(e)))
    );
    
const zoomInOutEpic = (action$, store) =>
    action$.ofType("ZOOM_IN_OUT").switchMap( action => {        
        let { riskAnalysis, context } = (store.getState()).disaster;         
        const resolvedContext = action && action.context || riskAnalysis && riskAnalysis.context;
        if(action.context != null) context = action.context.replace(/(ht\/\w+\/).*/, "$1");
        const analysisHref = riskAnalysis && `${action.dataHref}${resolvedContext}`;
        return Rx.Observable.defer(() => Api.getData(`${action.dataHref}${context || ''}`))
            .retry(1).
            map(data => [dataLoaded(data), getFeatures(action.geomHref)].concat(analysisHref && getAnalysisData(analysisHref) || []))
            .mergeAll()
            .startWith(dataLoading(true))
            .catch( () => Rx.Observable.of(info({title: "Info", message: "Analysis not available at requested zoom level", position: 'tc', autoDismiss: 3})));
    });       

const selectEventEpic = (action$, store) =>
    action$.ofType(SELECT_EVENT) 
        .map(action => {                           
            const { app, contextUrl, riskAnalysis, selectedEventIds, showEventDetail } = (store.getState()).disaster;             
            const urlPrefix = `${contextUrl}/${app}/data_extraction`;
            const fullContext = riskAnalysis && riskAnalysis.fullContext;
            if(showEventDetail) { 
                const { events } = action;               
                if(events.length > 1)
                    return [Rx.Observable.of(info({title: "Info", message: "Please, select a single event to view details", position: 'tc', autoDismiss: 3}))];
                const event = events[0];
                const eventHref = `${urlPrefix}/ht/${fullContext.ht}/an/${fullContext.an}/evt/${event}/`;
                return [eventDetails(eventHref)];
            }
            if(selectedEventIds !== undefined && selectedEventIds.length > 0) {                
                const { loc } = action;            
                const dataHref = `${urlPrefix}/loc/${loc}/`;
                const geomHref = `${urlPrefix}/geom/${loc}/`;
                const evtString = selectedEventIds.join("__");
                const eventHref = `${dataHref}lvl/${fullContext.adm_level}/ht/${fullContext.ht}/an/${fullContext.an}/evt/${evtString}/`;            
                return [getEventData(eventHref)];            
            }
            return [];
        })
        .mergeAll();
        
const setFiltersEpic = (action$, store) =>
    action$.ofType(SET_FILTERS)
        .map(action => [getAnalysisData(action.url)])
        .mergeAll();

const admLookupEpic = (action$, store) =>
    action$.ofType(ADM_LOOKUP).switchMap(action => {        
        return Rx.Observable.defer(() => Api.getData(action.url))
            .retry(1)
            .map(val => [admLookupLoaded(val, action.detail)])
            .mergeAll()
            .startWith(dataLoading(true))            
            .catch(e => Rx.Observable.of(dataError(e)))
    })

const switchContextAnalysisEpic = (action$, store) =>
    action$.ofType(SWITCH_CONTEXT).map(action => {
        const { contextUrl } = (store.getState()).disaster;         
        const dataHref = `${contextUrl}/risks/data_extraction/reg/${action.reg}/loc/${action.loc}/`;
        const geomHref = `${contextUrl}/risks/data_extraction/reg/${action.reg}/geom/${action.loc}/`;
        const context = `ht/${action.ht}/at/${action.at}/an/${action.an}/`;
        return [zoomInOut(dataHref, geomHref, context)];
    })
    .mergeAll();

const initStateEpic = action$ =>
    action$.ofType(INIT_RISK_APP) // Wait untile map config is loaded
        .audit( () => action$.ofType('MAP_CONFIG_LOADED'))
        .map(action => {
            const analysisHref = action.ac && `${action.href}${action.ac}`;
            return [getData(`${action.href}${action.gc || ''}`), getFeatures(action.geomHref)].concat(analysisHref && getAnalysisData(analysisHref) || [] );
        }).
        mergeAll();
const initStateEpicCost = action$ =>
            action$.ofType(INIT_RISK_APP) // Wait untile map config is loaded
                .audit( () => action$.ofType('MAP_CONFIG_LOADED'))
                .map(action => {
                    const analysisHref = action.ac && `${action.href}${action.ac}`;
                    return [getData(`${action.href}${action.gc || ''}`)].concat(analysisHref && getAnalysisData(analysisHref) || [] );
                }).
                mergeAll();
const changeTutorial = action$ =>
    action$.ofType(DATA_LOADED, ANALYSIS_DATA_LOADED, EVENT_DATA_LOADED).audit( () => action$.ofType('TOGGLE_CONTROL')).switchMap( action => {
        return Rx.Observable.of(action).flatMap((actn) => {
            // get current app and switch tutorial
            const {defaultStep, tutorialStep} = ConfigUtils.getConfigProp('tutorialPresets');
            let type = actn.data && actn.data.analysisType ? actn.type + '_R' : actn.type;
            return [setupTutorial(tutorialStep[type], {}, '', defaultStep)];
        });
    });
const loadingError = action$ =>
    action$.ofType(DATA_ERROR).map(
        action => error({title: "Loading error", message: action.error.message,
            autoDismiss: 3}));
const dataLoadingEpic = (action$) =>
    action$.ofType(DATA_LOADING)
        .map(action => { return [removeLayer('_riskAn_'), removeLayer('_eventAn_')] })
        .mergeAll();            
const getSpecificFurtherResources = (action$) =>
    action$.ofType(GET_S_FURTHER_RESOURCE_DATA).switchMap(action => {
        return Rx.Observable.defer(() => Api.getData(action.url))
            .retry(1)
            .delay(1000)
            .map( (val) => {
                const resource = val.furtherResources && val.furtherResources.hazardSet ? val.furtherResources.hazardSet : {};
                const actions = [info({uid: action.uid, children: makeNotificationBody(resource, action.title, action.head), position: 'bc', autoDismiss: 0})];
                return actions;
            })
            .mergeAll()
            .startWith(info({title: 'Loading', position: 'bc', autoDismiss: 2}))
            .catch(e => Rx.Observable.of(dataError(e)));
    });
const chartSliderUpdateEpic = action$ =>
    action$.ofType(CHART_SLIDER_UPDATE)
        .switchMap( action => Rx.Observable.of(setChartSliderIndex(action.index, action.uid))

    );

module.exports = {getRiskDataEpic, getRiskMapConfig, getRiskFeatures, getAnalysisEpic, getEventEpic, getEventDetailsEpic, admLookupEpic, selectEventEpic, setFiltersEpic, dataLoadingEpic, zoomInOutEpic, initStateEpic, changeTutorial, loadingError, getSpecificFurtherResources, chartSliderUpdateEpic, initStateEpicCost, switchContextAnalysisEpic};
