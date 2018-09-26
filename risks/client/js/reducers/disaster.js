/**
 * Copyright 2017, GeoSolutions Sas.
 * All rights reserved.
 *
 * This source code is licensed under the BSD-style license found in the
 * LICENSE file in the root directory of this source tree.
 */
const assign = require('object-assign');
const {
    DATA_LOADING,
    DATA_LOADED,
    DATA_ERROR,
    TOGGLE_DIM,
    ANALYSIS_DATA_LOADED,
    EVENT_DATA_LOADED,
    EVENT_DETAILS_LOADED,
    SET_DIM_IDX,    
    TOGGLE_ADMIN_UNITS,
    GET_ANALYSIS_DATA,
    GET_EVENT_DATA,
    SET_CHART_SLIDER_INDEX,
    SET_ADDITIONAL_CHART_INDEX,
    TOGGLE_SWITCH_CHART,
    ZOOM_IN_OUT,
    SET_ANALYSIS_CLASS,  
    SELECT_EVENT,
    SET_FILTERS,
    ADM_LOOKUP_LOADED,
    TOOGLE_EVENT_DETAIL,
    TOOGLE_EVENT_DETAIL_V   
} = require('../actions/disaster');

function disaster(state = {dim: {dim1: 0, dim2: 1, dim1Idx: 0, dim2Idx: 0}}, action) {
    switch (action.type) {
        case DATA_LOADING:
            return assign({}, state, {
                loading: true
            });
        case DATA_LOADED: {
            return action.cleanState ? assign({}, {showSubUnit: true, loading: false, error: null, app: state.app, analysisClass: state.analysisClass, contextUrl: state.contextUrl, region: state.region}, action.data) : assign({}, {showSubUnit: state.showSubUnit, loading: false, error: null, dim: state.dim, selectedEventIds: state.selectedEventIds, analysisClass: state.analysisClass, analysisFilters: state.analysisFilters, sliders: state.sliders, riskAnalysis: state.riskAnalysis, app: state.app, contextUrl: state.contextUrl, region: state.region}, action.data);
        }
        case ANALYSIS_DATA_LOADED: {
            return assign({}, state, { loading: false, error: null, riskAnalysis: action.data, cValues: action.data.riskAnalysisData.data.values, zoomJustCalled: 2, lookupResultsDetail: [], lookupResults: []});
        }
        case EVENT_DATA_LOADED: {            
            return assign({}, state, { loading: false, error: null, eventAnalysis: action.data, cValues: action.data.eventValues });
        }
        case EVENT_DETAILS_LOADED: {
            return assign({}, state, { loading: false, error: null, eventDetails: action.data });
        }
        case TOGGLE_DIM: {
            const newDim = state.dim && {dim1: state.dim.dim2, dim2: state.dim.dim1, dim1Idx: state.dim.dim2Idx, dim2Idx: state.dim.dim1Idx} || {dim1: 1, dim2: 0, dim1Idx: 0, dim2Idx: 0};
            return assign({}, state, {dim: newDim, sliders: {}});
        }
        case TOGGLE_ADMIN_UNITS: {
            return assign({}, state, {showSubUnit: !state.showSubUnit});
        }
        case SET_DIM_IDX: {
            const newDim = assign({dim1: 0, dim2: 1, dim1Idx: 0, dim2Idx: 0}, state.dim, {[action.dim]: action.idx});            
            return assign({}, state, {dim: newDim});
        }        
        case DATA_ERROR:
            return assign({}, state, {
                error: action.error,
                loading: false
            });
        case GET_ANALYSIS_DATA:
            return assign({}, state, {
                currentAnalysisUrl: action.url
            });
        case GET_EVENT_DATA:
            return assign({}, state, {
                currentAnalysisUrl: action.url
            });
        case SET_CHART_SLIDER_INDEX:
            let sliders = assign({}, state.sliders);
            sliders[action.uid] = action.index;
            return assign({}, state, {
                sliders
            });
        case SET_ADDITIONAL_CHART_INDEX:
            let additionalCharts = {currentSection: action.section, currentCol: action.col, currentTable: action.table};
            return assign({}, state, {
                additionalCharts
            });
        case TOGGLE_SWITCH_CHART: {
            return assign({}, state, {showChart: !state.showChart});
        }
        case ZOOM_IN_OUT: {
            return assign({}, state, {selectedEventIds: [], zoomJustCalled: 1});
        }  
        case SET_ANALYSIS_CLASS: {
            return assign({}, state, { analysisClass: action.value });
        }          
        case SELECT_EVENT: {              
            if(state.showEventDetail)
                return assign({}, state, { eventDetails: {}, visibleEventDetail: true });
            const { events, isSelected } = action;                        
            let ids = state && state.selectedEventIds || [];            
            //set the array of ids             
            if(typeof events !== undefined && events.length > 1) {
                ids = isSelected ? events : [];                    
            }
            else if(events.length > 0) {                
                ids = isSelected ? [...ids, events[0]] : ids.filter(item => item !== events[0]);
            }                        
            ids = ids.filter((v, i, a) => a.indexOf(v) === i);                        
            return assign({}, state, { selectedEventIds: ids, zoomJustCalled: 1 });
        } 
        case SET_FILTERS: {
            const { analysisFilters } = action;            
            return assign({}, state, { analysisFilters });
        }  
        case ADM_LOOKUP_LOADED: {               
            const newState = action.detail ? { lookupResultsDetail: action.val } : { lookupResults: action.val, lookupResultsDetail: [] };
            return assign({}, state, newState);
        }  
        case TOOGLE_EVENT_DETAIL: {
            return assign({}, state, { showEventDetail: !state.showEventDetail });
        } 
        case TOOGLE_EVENT_DETAIL_V: {
            return assign({}, state, { visibleEventDetail: !state.visibleEventDetail });
        }        
        default:
            return state;
    }
}

module.exports = disaster;
