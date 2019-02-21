const {createSelector} = require('reselect');
const {last, head, isNull} = require('lodash');
const url = require('url');
const navItemsSel = ({disaster = {}}) => disaster.navItems || [];
const riskItemsSel = ({disaster = {}}) => disaster.overview || {};
const activeFiltersSel = ({disaster = {}}) => disaster.activeFilters || {};
const hazardTypeSel = ({disaster = {}}) => disaster.hazardType || {};
const analysisTypeSel = ({disaster = {}}) => disaster.analysisType || {};
const sliderSel = ({disaster = {}}) => disaster.sliders || {};
const notificationsSel = (state) => state.notifications || [];
const currentAnalysisUrlSel = ({disaster = {}}) => disaster.currentAnalysisUrl || '';
const additionalChartsSel = ({disaster = {}}) => disaster.additionalCharts || {};
const riskAnalysisDataSel = ({disaster = {}}) => disaster.riskAnalysis && disaster.riskAnalysis.riskAnalysisData || {};
const fullContextSel = ({disaster = {}}) => disaster.riskAnalysis && disaster.riskAnalysis.fullContext || {};
const dimInit = {dim1: 0, dim2: 1, dim1Idx: 0, dim2Idx: 0};
const dimSelector = ({disaster = {}}) => disaster.dim || dimInit;
const loadingStateSelector = ({disaster = {}}) => disaster.loading;
//const eventSelector = ({disaster = {}}) => disaster.riskEvent || {};
//const eventsSelector = ({disaster = {}}) => disaster.riskAnalysis && disaster.riskAnalysis.riskAnalysisData && disaster.riskAnalysis.riskAnalysisData.events || {};
const selectedEventsSelector = ({disaster = {}}) => disaster.selectedEventIds || [];
//const analysisFiltersSel = ({disaster = {}}) => disaster.analysisFilters || { from: '', to: '' };
const chartValues = ({disaster = {}}) => disaster.cValues || [];
const showChartSel = ({disaster = {}}) => disaster.showChart || false;
const contextSel = ({disaster = {}}) => disaster.context && !isNull(disaster.context) && disaster.context || '';
const riskAnalysisContextSelector = ({disaster = {}}) => disaster.riskAnalysis && disaster.riskAnalysis.context;
const analysisClassSelector = ({disaster = {}}) => disaster.analysisClass || '';
const zoomJustCalledSel = ({disaster = {}}) => disaster.zoomJustCalled || 0;
const admLookupSel = ({disaster = {}}) => disaster.lookupResults || [];
const showFiltersSel = ({disaster = {}}) => disaster.showFilters !== undefined ? disaster.showFilters : true;
const filteredAnalysisSel = ({disaster = {}}) => disaster.filteredAnalysis || null; 
const showEventDetailSel = ({disaster = {}}) => disaster.showEventDetail || false;
const visibleEventDetailSel = ({disaster = {}}) => disaster.visibleEventDetail || false;
//const eventDetailsSel = ({disaster = {}}) => disaster.eventDetails || {};
const contextUrlPrefixSel = ({disaster = {}}) => disaster.contextUrl || '';
const activeRegionSel = ({disaster = {}}) => disaster.disasterRisk && disaster.disasterRisk.app && disaster.disasterRisk.app.regionName || '';
const currentAdminUnitsSel = ({disaster = {}}) => disaster.currentAdminUnits || [];
const topBarSelector = createSelector([navItemsSel, riskItemsSel, hazardTypeSel, contextSel],
     (navItems, riskItems, hazardType, context) => ({
        navItems,
        title: (last(navItems) || {label: ''}).label,
        overviewHref: (last(navItems) || {href: ''}).href,
        riskItems,
        activeRisk: hazardType,
        context,
        showHazard: hazardType.mnemonic ? true : false,
    }));

const prepareEventData = ({disaster = {}}) => {    
    const eventAnalysisData = disaster && disaster.riskAnalysis && disaster.riskAnalysis.riskAnalysisData && disaster.riskAnalysis.riskAnalysisData.events || [];
    const eventDataSources = disaster && disaster.riskAnalysis && disaster.riskAnalysis.riskAnalysisData && disaster.riskAnalysis.riskAnalysisData.eventDataSources || [];
    
    if(eventAnalysisData && eventAnalysisData.length > 0) {
        return eventAnalysisData.map(e => {                 
            const dataKey = e && e.dim1 && e.dim1.value;                
            const values_list = e && e.values && e.values[0]; //TODO: process data for all phenomena instead of considering only event
            values_list.sort((a,b) => (a.insert_date < b.insert_date) ? 1 : ((b.insert_date < a.insert_date) ? -1 : 0));
            let value = null;
            let dataSource = null;
            for(let ds of eventDataSources) {
                if(value)
                    break;
                for(let val of values_list) {                                    
                    if(val.data_source == ds.name) {
                        value = parseFloat(val.value_event);
                        dataSource = val.data_source;
                        break;
                    }                        
                }
            }                        
            const timestamp = e && e.timestamp;
            const event_source = e && e.event && e.event.event_source || '';
            const sources = e && e.event && e.event.sources || '';
            const adm_divisions = e && e.adm_divisions && e.adm_divisions.map(a => { return {code: a.code, name: a.name }}) || [];                        
            return { ...e.event, dataKey, value, dataSource, timestamp, event_source, sources, adm_divisions }
        })
    }
    return eventAnalysisData;
}

const eventDetailsSel = ({disaster = {}}) => {
    const eventDetails = disaster.eventDetails || {};        
    const { data, dataSources } = eventDetails;
    if(data !== undefined) {
        let adjustedData = {};
        Object.keys(data).map( key => {
            adjustedData[key] = data[key];            
            let adjustedValues = [];
            const { dim1, dim2, values } = data[key] && data[key].values;
            const { relatedRiskAnalysis } = data[key];
            if(values !== undefined && values.length > 0) {
                let value = null;
                for(let i in dataSources) {
                    if(!value) {
                        const matches = values[0].filter(v => v.data_source === dataSources[i])
                        if(matches.length > 0)
                            value = matches[0].value_event;
                    }                        
                    else
                        break;
                }
                adjustedValues.push([dim1.value, dim2.value, parseFloat(value)]);
                if(relatedRiskAnalysis.length > 0) {
                    const { values } = relatedRiskAnalysis[0];
                    const newValues = values.filter(d => d.dim1 === dim1.value || d.dim1 === 'Total').map(v => [dim1.value, v.dim2, v.value]);
                    for(let i in newValues)
                        adjustedValues.push(newValues[i])
                }                                   
                adjustedData[key]['values'] = adjustedValues;
            }
        });        
        return { overview: eventDetails.overview, dataSources: eventDetails.dataSources, data: adjustedData}
    }    
    return eventDetails;
}

const dataContainerSelector = createSelector(
    [
        navItemsSel,
        riskItemsSel,
        hazardTypeSel,
        analysisTypeSel,
        riskAnalysisDataSel,
        dimSelector,
        loadingStateSelector,
        showChartSel,
        fullContextSel,
        analysisClassSelector,
        zoomJustCalledSel,
        chartValues,
        selectedEventsSelector,
        contextUrlPrefixSel,
        filteredAnalysisSel,
        activeFiltersSel,
        showFiltersSel,
        prepareEventData,
        currentAdminUnitsSel
    ],
    (
        navItems,
        riskItems,
        hazardType,
        analysisType,
        riskAnalysisData,
        dim,
        loading,
        showChart,
        fullContext,
        analysisClass,
        zoomJustCalled,
        cValues,
        selectedEventIds,
        contextUrl,
        filteredAnalysis,
        activeFilters,
        showFilters,
        eventAnalysisData,
        currentAdminUnits
    ) => 
    ({
        navItems,
        overviewHref: (last(navItems) || {href: ''}).href,        
        riskItems,        
        activeRisk: hazardType.mnemonic || "Overview",
        showHazard: hazardType.mnemonic ? true : false,
        hazardTitle: hazardType.mnemonic ? head(riskItems['hazardType'].filter((hz) => hz.mnemonic === hazardType.mnemonic)).title || '' : '',
        hazardType,
        analysisType,        
        riskAnalysisData,
        dim,
        loading,
        showChart,
        fullContext,
        analysisClass,        
        zoomJustCalled,
        cValues,
        selectedEventIds,
        contextUrl,
        filteredAnalysis,
        activeFilters,
        showFilters,
        eventAnalysisData,
        currentAdminUnits
    }));
const drillUpSelector = createSelector([navItemsSel],
     (navItems) => ({
        disabled: navItems.length < 2,
        label: navItems.length > 1 ? (navItems[navItems.length - 2]).label : '',
        href: navItems.length > 1 ? (navItems[navItems.length - 2]).href : '',
        geom: navItems.length > 1 ? (navItems[navItems.length - 2]).geom : ''
    }));
const switchDimSelector = createSelector([riskAnalysisDataSel, dimSelector],
    (riskAnalysisData, dim) => ({
    dimName: riskAnalysisData.data && riskAnalysisData.data.dimensions && riskAnalysisData.data.dimensions[dim.dim2].name
    }));
const axesSelector = createSelector([riskAnalysisDataSel, dimSelector],
    (riskAnalysisData, dim) => ({
    dimension: riskAnalysisData.data && riskAnalysisData.data.dimensions && riskAnalysisData.data.dimensions[dim.dim2],
        activeAxis: dim.dim2Idx
    }));
const shareUrlSelector = createSelector([navItemsSel, contextSel, riskAnalysisContextSelector, dimSelector, sliderSel],
    (navItems, context, riskAnalysisContext, dim, slider) => {
        const {host, pathname, protocol} = url.parse(window.location.href, false);
        const init = JSON.stringify({href: (last(navItems) || {href: ''}).href, geomHref: (last(navItems) || {geom: ''}).geom, gc: context, ac: riskAnalysisContext, d: dim, s: slider});
        return {shareUrl: `${protocol}//${host}${pathname}?init=${encodeURIComponent(init)}`};
    });
const downloadDataSelector = createSelector([notificationsSel, riskAnalysisDataSel],
    (notifications, riskAnalysisData) => (
      {
        download: notifications.filter((val) => { return val.uid === 'download_tab'; }),
        riskAnalysisData
      })
    );
const moreInfoSelector = createSelector([notificationsSel, riskAnalysisDataSel],
    (notifications, riskAnalysisData) => (
      {
        moreInfo: notifications.filter((val) => { return val.uid === 'more_info_tab'; }),
        riskAnalysisData
      })
    );
const labelSelector = createSelector([notificationsSel, currentAnalysisUrlSel],
      (notifications, currentUrl) => (
        {
          notifications,
          currentUrl
        })
      );
const chartSelector = createSelector([riskAnalysisDataSel, dimSelector, fullContextSel, chartValues],
    (riskAnalysisData, dim, fullContext, cValues) => ({
        //values: riskAnalysisData.data && riskAnalysisData.data.values,
        values: cValues,
        dimension: riskAnalysisData.data && riskAnalysisData.data.dimensions,
        val: riskAnalysisData.data && riskAnalysisData.data.dimensions && riskAnalysisData.data.dimensions[dim.dim1].values[dim.dim1Idx],
        dim,
        uOm: riskAnalysisData.unitOfMeasure || 'Values',
        full_context: fullContext
    }));
const sliderSelector = createSelector([riskAnalysisDataSel, dimSelector, sliderSel, notificationsSel, currentAnalysisUrlSel],
    (riskAnalysisData, dim, sliders, notifications, currentUrl) => ({
        dimension: riskAnalysisData.data && riskAnalysisData.data.dimensions && riskAnalysisData.data.dimensions[dim.dim2],
        activeAxis: dim.dim2Idx,
        sliders,
        notifications,
        currentUrl
    }));
const mapSliderSelector = createSelector([riskAnalysisDataSel, dimSelector, sliderSel, notificationsSel, currentAnalysisUrlSel],
    (riskAnalysisData, dim, sliders, notifications, currentUrl) => ({
        dimension: riskAnalysisData.data && riskAnalysisData.data.dimensions && riskAnalysisData.data.dimensions[dim.dim1],
        activeAxis: dim.dim1Idx,
        sliders,
        notifications,
        currentUrl
    }));
const sliderChartSelector = createSelector([riskAnalysisDataSel, dimSelector, sliderSel],
    (riskAnalysisData, dim, sliders) => ({
        values: riskAnalysisData.data && riskAnalysisData.data.values,
        dimension: riskAnalysisData.data && riskAnalysisData.data.dimensions,
        val: riskAnalysisData.data && riskAnalysisData.data.dimensions && riskAnalysisData.data.dimensions[dim.dim1].values[dim.dim1Idx],
        dim,
        uOm: riskAnalysisData.unitOfMeasure || 'Values',
        sliders
    }));
const additionalChartSelector = createSelector([riskAnalysisDataSel, additionalChartsSel],
    (riskAnalysisData, additionalCharts) => ({
        tables: riskAnalysisData.additionalTables || [],
        currentCol: additionalCharts.currentCol,
        currentSection: additionalCharts.currentSection,
        currentTable: additionalCharts.currentTable
    }));
const lookupResultsSelector = createSelector([admLookupSel, contextUrlPrefixSel, activeRegionSel, activeFiltersSel],
    (lookupResults, contextUrl, region, activeFilters) => ({
        lookupResults,        
        contextUrl,
        region,
        activeFilters
    }));
const eventDetailsSelector = createSelector([eventDetailsSel, dimSelector, riskAnalysisDataSel, showEventDetailSel, visibleEventDetailSel],
    (eventDetails, dim, riskAnalysisData, showEventDetail, visibleEventDetail) => ({
        eventDetails,
        dim,
        riskAnalysisData,
        showEventDetail,
        visibleEventDetail
    }));
const contextUrlPrefixSelector = createSelector([contextUrlPrefixSel],
    (contextUrl) => ({
        contextUrl
    }));

module.exports = {
    dimSelector,    
    drillUpSelector,
    topBarSelector,
    dataContainerSelector,
    switchDimSelector,
    axesSelector,
    shareUrlSelector,
    downloadDataSelector,
    moreInfoSelector,
    labelSelector,
    chartSelector,
    sliderSelector,
    mapSliderSelector,
    sliderChartSelector,
    additionalChartSelector,
    lookupResultsSelector,
    eventDetailsSelector,
    contextUrlPrefixSelector,
    prepareEventData
};
