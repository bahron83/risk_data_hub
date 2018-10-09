import React, { Component } from 'react';
import { connect } from 'react-redux';
import { dataContainerSelector, chartSelector, eventTableSelector, sChartSelector, eventCountryChartSelector } from '../selectors/disaster';
import { getAnalysisData, getData, setDimIdx, getEventData, getSFurtherResourceData, zoomInOut, setAnalysisClass, selectEvent, setFilters } from '../actions/disaster';
import Chart from '../components/Chart';
import EventCountryChart from '../components/EventCountryChart';
import SendaiCountryChart from '../components/SendaiCountryChart';
import SChart from '../components/ScatterChart';
import EventTable from '../components/EventTable';
import Paginator from '../components/Paginator';
import DatePickerRange from '../components/DatePickerRange';
import Search from '../components/Search';
const SummaryChart = connect(chartSelector)(require('../components/SummaryChart'));
const GetAnalysisBtn = connect(({disaster}) => ({loading: disaster.loading || false}))(require('../components/LoadingBtn'));

import DownloadData from '../components/DownloadData';
import MoreInfo from '../components/MoreInfo';
const Overview = connect(({disaster = {}}) => ({riskItems: disaster.overview || [] }) )(require('../components/Overview'));
import { Panel, Tooltip, OverlayTrigger } from 'react-bootstrap';
import Nouislider from 'react-nouislider';
import { show, hide } from 'react-notification-system-redux';
import { labelSelector } from '../selectors/disaster';
const LabelResource = connect(labelSelector, { show, hide, getData: getSFurtherResourceData })(require('../components/LabelResource'));
import { generateReport } from '../actions/report';
const DownloadBtn = connect(({disaster, report}) => {
    return {
        active: disaster.riskAnalysis && disaster.riskAnalysis.riskAnalysisData && true || false,
        downloading: report.processing
    };
}, {downloadAction: generateReport})(require('../components/DownloadBtn'));


const DEFAULT_DECIMAL_POINTS = 3;

class DataContainer extends Component {            
    
    round(value) {
        const decimals = this.props && this.props.riskAnalysisData && this.props.riskAnalysisData.decimalPoints || DEFAULT_DECIMAL_POINTS;        
        const adjustedValue = value.toString().indexOf('e') > -1 ? value : value+'e'+decimals;        
        return Number(Math.round(adjustedValue)+'e-'+decimals);
    }
    
    getRandomColor() {
        const letters = '0123456789ABCDEF';
        let color = '#';
        for (let i = 0; i < 6; i++ ) {
            color += letters[Math.floor(Math.random() * 16)];
        }
        return color;
    }

    getChartData(data, val) {
        const {dim} = this.props;
        const nameIdx = dim === 0 ? 1 : 0;
        return data.filter((d) => d[nameIdx] === val ).map((v) => {return {"name": v[dim], "value": parseInt(v[2], 10)}; });
    }    
    
    prepareEventData() {            
        //return this.props.riskAnalysisData && this.props.riskAnalysisData.events || [];
        const { fullContext } = this.props;
        const events = this.props.riskAnalysisData && this.props.riskAnalysisData.events || [];
        return events.map(v => {
            let newObj = v;
            newObj['details_link'] = `<a href="/risks/data_extraction/an/${fullContext.an}/evt/${v.event_id}">click</a>`;
            return newObj;
        });

        /*const { event_values: values } = this.props.riskAnalysisData.data || null;
        if(events && values) {
            const dataKey = Object.entries(values)[0][1][1];  
            return(
                events.map(v => {
                    let newObj = v;
                    const valueArr = values[v['event_id']];                            
                    newObj[dataKey] = (valueArr && valueArr[3]) ? !isNaN(parseFloat(valueArr[3])) ? parseFloat(valueArr[3]) : null : null;
                    newObj['data_key'] = dataKey;
                    return newObj;              
                })  
            );
        }
        return [];*/        
        //return events;
    }

    filterByLoc(data) {        
        const ctx = this.props.fullContext;
        if(ctx.adm_level > 0 && data != null)
            return data.filter(e => e.iso2 == ctx.loc);
        return data;
    }

    filterByDate(begin, end) {
        const { events } = this.props.riskAnalysisData;
        if(events) {

        }
    }
    
    selectRP(item, index) {
        const { fullContext, setDimIdx, getAnalysis } = this.props;
        setDimIdx('dim2Idx', index);
        getAnalysis(fullContext.full_url);
    }    

    renderAnalysisData() {        
        const { dim, loading, fullContext, analysisType, analysisTypeE, selectedEventIds, cValues, zoomInOut, selectEvent, setFilters, getAnalysis, contextUrl } = this.props;                
        const { hazardSet, data } = this.props.riskAnalysisData;             
        const { unitOfMeasure } = this.props.riskAnalysisData || 'Values';
        const tooltip = (<Tooltip id={"tooltip-back"} className="disaster">{'Back to Analysis Table'}</Tooltip>);
        const val = data.dimensions[dim.dim1].values[dim.dim1Idx];
        const header = data.dimensions[dim.dim1].name + ': ' + val;
        const description = data.dimensions[dim.dim1].layers && data.dimensions[dim.dim1].layers[val] && data.dimensions[dim.dim1].layers[val].description ? data.dimensions[dim.dim1].layers[val].description : '';
        const eventData = this.prepareEventData();               
        const { event_group_country: eventDataGroup, dimensions: dimension } = this.props.riskAnalysisData && this.props.riskAnalysisData.data;        
        let selectedAnalysisType = analysisType;                 

        if(this.props.analysisClass == (analysisTypeE && analysisTypeE.analysisClass && analysisTypeE.analysisClass.name))            
            selectedAnalysisType = analysisTypeE;
        return (
            <div id="disaster-analysis-data-container" className="container-fluid">
                <div className="row">
                    <div className="btn-group">
                        <OverlayTrigger placement="bottom" overlay={tooltip}>
                            <button id="disaster-back-button" onClick={()=> this.props.getData(selectedAnalysisType.href, true)} className="btn btn-primary">
                                <i className="fa fa-arrow-left"/>
                            </button>
                        </OverlayTrigger>
                        <MoreInfo/>
                    </div>
                    <div className="btn-group pull-right">
                        <DownloadBtn/>
                        <DownloadData/>
                    </div>
                </div>
                <div className="row">
                    <h4 style={{margin: 0}}>{hazardSet.title}</h4>
                </div>
                <div className="row">
                    <p>{hazardSet.purpose}</p>
                </div>
                <div id="disaster-chart-container" className="row">
                    {data.dimensions[dim.dim1].values.length - 1 === 0 ? (
                    <LabelResource uid={'chart_label_tab'} description={description} label={header} dimension={data.dimensions[dim.dim1]}/>
                    ) : (
                    <div>
                        <LabelResource uid={'chart_label_tab'} description={description} label={header} dimension={data.dimensions[dim.dim1]}/>
                        <div className="slider-box">
                            <Nouislider
                                range={{min: 0, max: data.dimensions[dim.dim1].values.length - 1}}
                                start={[dim.dim1Idx]}
                                step={1}
                                tooltips={false}
                                onChange={(idx) => {this.props.setDimIdx('dim1Idx', Number.parseInt(idx[0])); getAnalysis(fullContext.full_url); }}
                                pips= {{
                                    mode: 'steps',
                                    density: 20,
                                    format: {
                                        to: (value) => {
                                            let valF = data.dimensions[dim.dim1].values[value].split(" ")[0];
                                            return valF.length > 8 ? valF.substring(0, 8) + '...' : valF;
                                        },
                                        from: (value) => {
                                            return value;
                                        }
                                    }
                                }}/>
                        </div>
                    </div>
                    )}

                    {(contextUrl == null || contextUrl == '') ? (
                        <Panel className="panel-box">
                            <h4>Search a name (country, nuts3 or city)</h4>
                            <Search />                        
                        </Panel>
                    ) : null
                    }
                    
                    
                    {fullContext.analysis_class == 'event' ? (                        
                        <div>
                            {fullContext.adm_level > 0 ? (
                                <Panel className="panel-box">   
                                    <h4 className="text-center">{'Sendai Target Indicator'}</h4>                             
                                    <SendaiCountryChart dim={dim} data={data} unitOfMeasure={unitOfMeasure} round={this.round.bind(this)}/>
                                </Panel>
                            ) : (
                                <Panel className="panel-box">   
                                    <h4 className="text-center">{'Historical Events Chart'}</h4>                             
                                    <EventCountryChart data={eventDataGroup} uOm={unitOfMeasure} fullContext={fullContext} zoomInOut={zoomInOut} contextUrl={contextUrl}/>
                                </Panel>
                            )}
                            
                            <Panel className="panel-box">                                
                                <h4>Filter by date</h4>                                
                                <DatePickerRange fullContext={fullContext} setFilters={setFilters} loading={loading}/>
                            </Panel>
                            <Panel className="panel-box">
                                <h4 className="text-center">{'Historical Events Chart'}</h4>
                                <SChart data={eventData} unitOfMeasure={unitOfMeasure} selectEvent={selectEvent} selectedEventIds={selectedEventIds} fullContext={fullContext}/>  
                                <Paginator total={data.total_events} showing={eventData.length} fullContext={fullContext} getAnalysisData={getAnalysis} loading={loading}/>                               
                            </Panel>
                            <Panel className="panel-box">
                                <h4 className="text-center">{'Historical Events Resume'}</h4>
                                <EventTable data={eventData} unitOfMeasure={unitOfMeasure} selectEvent={selectEvent} selectedEventIds={selectedEventIds} fullContext={fullContext}/>
                                <Paginator total={data.total_events} showing={eventData.length} fullContext={fullContext} getAnalysisData={getAnalysis} loading={loading}/>
                            </Panel>                                                                               
                        </div>
                    ) : (
                        <div>                            
                            <Panel className="panel-box">
                                <h4 className="text-center">{'Current ' + data.dimensions[dim.dim1].name + ' Chart'}</h4>
                                <Chart dim={dim} values={cValues} val={val} dimension={dimension} uOm={unitOfMeasure} selectRP={this.selectRP.bind(this)}/>
                            </Panel>                                        
                            <SummaryChart/>
                        </div>
                    )}
                    
                </div>
            </div>
        );
    }

    renderRiskAnalysisHeader(title, getAnalysis, rs, idx) {
        const tooltip = (<Tooltip id={"tooltip-abstract-" + idx} className="disaster">{'Show Abstract'}</Tooltip>);
        return (
          <OverlayTrigger placement="top" overlay={tooltip}>
          <div className="row">
            <div className="col-xs-10">
              <div className="disaster-analysis-title">{title}</div>
            </div>
            <div className="col-xs-2">
                <i className="pull-right fa fa-chevron-down"></i>
            </div>
          </div>
          </OverlayTrigger>
        );
    }

    renderRiskAnalysis() {
        const {analysisType = {}, analysisTypeE = {}, getAnalysis} = this.props;        
        let selectedAnalysisType = analysisType;            
        if(this.props.analysisClass == (analysisTypeE && analysisTypeE.analysisClass && analysisTypeE.analysisClass.name) || (this.props.analysisClass == '' && analysisType == {}))            
            selectedAnalysisType = analysisTypeE;         
        return (selectedAnalysisType.riskAnalysis || []).map((rs, idx) => {
            const {title, fa_icon: faIcon, abstract} = rs.hazardSet;
            const tooltip = (<Tooltip id={"tooltip-icon-cat-" + idx} className="disaster">{'Analysis Data'}</Tooltip>);
            return (
                <div key={idx} className="row">
                    <div className="col-xs-1 text-center">
                        <OverlayTrigger placement="bottom" overlay={tooltip}>
                        <i className={'disaster-category fa ' + faIcon} onClick={()=> getAnalysis(rs.href)}></i>
                        </OverlayTrigger>
                    </div>
                    <div className="col-xs-11">
                    <Panel collapsible header={this.renderRiskAnalysisHeader(title, getAnalysis, rs, idx)}>
                        {abstract}
                        <br/>
                        <GetAnalysisBtn onClick={()=> getAnalysis(rs.href)}
                        iconClass="fa fa-bar-chart" label="Analysis Data"/>
                    </Panel>
                    </div>
                </div>
            );
        });        
    }

    renderAnalysisTab() {
        const {hazardType = {}, analysisType = {}, analysisTypeE = {}, getData: loadData} = this.props;
                        
        return (hazardType.analysisTypes || []).map((type, idx) => {
            const {href, name, title, faIcon, description, analysisClass} = type;
            const active = ((name === analysisType.name && analysisClass.name == this.props.analysisClass) || (name === analysisTypeE.name && analysisClass.name == this.props.analysisClass));
            const tooltip = (<Tooltip id={"tooltip-icon-analysis-tab-" + idx} className="disaster">{description}</Tooltip>);
            if(analysisClass.name == this.props.analysisClass) {                                
                return (                                
                    <OverlayTrigger key={name} placement="bottom" overlay={tooltip}>
                        <li key={name} className={`text-center ${active ? 'active' : ''}`} onClick={() => loadData(href, true)}>
                            <a href="#" data-toggle="tab"><span> <i className={"fa fa-" + faIcon}></i>&nbsp;{title}</span></a>
                        </li>
                    </OverlayTrigger>                
                );
            }
            return null;
        });
    }

    renderAnalysisClass() {        
        const {hazardType} = this.props;
        let analysisClasses = [];
        hazardType.analysisTypes.map((item, idx) => {
            analysisClasses.push(item.analysisClass);
        });
        analysisClasses = analysisClasses.filter((item, idx, self) =>
            idx === self.findIndex((t) => (
                t.name === item.name
            ))
        );        
        return(analysisClasses).map((item, idx) => {
            if(item != undefined && item != null) {
                const active = item.name == this.props.analysisClass;                                 
                return (
                    <li key={item.name} className={`text-center ${active ? 'active' : ''}`} onClick={() => this.props.setAnalysisClass(item.name)}>
                        <a href="#" data-toggle="tab"><span>{item.title}</span></a>
                    </li>
                );
            }
            return null;
        });
    } 

    renderHazard() {
        const {riskAnalysisData} = this.props;        
        return (//<div className={this.props.className}>
                <div className="disaster-header">
                  {riskAnalysisData.name ? (
                    <div className="container-fluid">
                        {this.renderAnalysisData()}
                    </div>
                  ) : (
                    <div className="container-fluid">
                        <ul id="disaster-analysis-class-menu" className="nav nav-pills">
                            {this.renderAnalysisClass()}
                        </ul>                                                
                        
                        <hr />
                        <ul id="disaster-analysis-menu" className="nav nav-pills">
                            {this.renderAnalysisTab()}
                        </ul>
                        
                        <hr></hr>
                        <div id="disaster-analysis-container" className="disaster-analysis">
                            <div className="container-fluid">
                                {this.renderRiskAnalysis()}
                            </div>
                        </div>
                    </div>
                  )
                  }
                </div>
            //</div>
        );
    }

    render() {
        const {showHazard, getData: loadData } = this.props;                
        return showHazard ? this.renderHazard() : (<Overview className={this.props.className} getData={loadData}/>);
    }

    componentDidMount() {
        this.componentDidUpdate();
    }

    componentDidUpdate() {
        const { analysisType = {}, analysisTypeE = {}, selectedEventIds = [], fullContext, zoomJustCalled, analysisClass, setAnalysisClass, selectEvent } = this.props;        

        let count = 0;
        if(analysisType.name == undefined)
            count += 1;
        if(analysisTypeE.name == undefined)
            count += 2;
                
        switch(count) {
            case 0:
                if(analysisClass == '')
                    setAnalysisClass('risk')
                break;
            case 1:
                if(analysisClass != 'event')
                    setAnalysisClass('event')
                break;
            case 2:
                if(analysisClass != 'risk')
                    setAnalysisClass('risk')
                break;            
        } 
                        
        if(selectedEventIds.length == 0 && fullContext.adm_level > 0 && zoomJustCalled == 2 && analysisClass == 'event') {            
            const eventData = this.prepareEventData();                
            if(eventData.length > 0)                                 
                selectEvent([eventData[0].event_id], true, fullContext.loc);
        }
    }
}

export default connect(dataContainerSelector, {getAnalysis: getAnalysisData, getData, setDimIdx, selectEvent, getEventData, zoomInOut, setAnalysisClass, setFilters})(DataContainer);
