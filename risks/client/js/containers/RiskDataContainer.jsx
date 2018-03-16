/**
 * Copyright 2017, GeoSolutions Sas.
 * All rights reserved.
 *
 * This source code is licensed under the BSD-style license found in the
 * LICENSE file in the root directory of this source tree.
 */
const React = require('react');
const {connect} = require('react-redux');
const {dataContainerSelector, chartSelector, eventTableSelector, sChartSelector, eventCountryChartSelector} = require('../selectors/disaster');

const {getAnalysisData, getData, setDimIdx, setEventIdx, getEventData, getSFurtherResourceData} = require('../actions/disaster');
const Chart = connect(chartSelector, {setDimIdx, getAnalysisData})(require('../components/Chart'));
const EventCountryChart = connect(eventCountryChartSelector, {getAnalysisData})(require('../components/EventCountryChart'));
const EventTable = connect(eventTableSelector, {setEventIdx, getEventData})(require('../components/EventTable'));
const SummaryChart = connect(chartSelector)(require('../components/SummaryChart'));
const ScatterChart = connect(sChartSelector, {setEventIdx, getEventData})(require('../components/ScatterChart'));
const GetAnalysisBtn = connect(({disaster}) => ({loading: disaster.loading || false}))(require('../components/LoadingBtn'));

const DownloadData = require('../components/DownloadData');
const MoreInfo = require('../components/MoreInfo');
const Overview = connect(({disaster = {}}) => ({riskItems: disaster.overview || [] }) )(require('../components/Overview'));
const {Panel, Tooltip, OverlayTrigger} = require('react-bootstrap');
const Nouislider = require('react-nouislider');
const {show, hide} = require('react-notification-system-redux');
const {labelSelector} = require('../selectors/disaster');
const LabelResource = connect(labelSelector, { show, hide, getData: getSFurtherResourceData })(require('../components/LabelResource'));
const {generateReport} = require('../actions/report');
const DownloadBtn = connect(({disaster, report}) => {
    return {
        active: disaster.riskAnalysis && disaster.riskAnalysis.riskAnalysisData && true || false,
        downloading: report.processing
    };
}, {downloadAction: generateReport})(require('../components/DownloadBtn'));

const DataContainer = React.createClass({
    propTypes: {
        getData: React.PropTypes.func,
        getAnalysis: React.PropTypes.func,
        setDimIdx: React.PropTypes.func,
        setEventIdx: React.PropTypes.func,
        showHazard: React.PropTypes.bool,
        className: React.PropTypes.string,
        hazardTitle: React.PropTypes.string,
        analysisType: React.PropTypes.object,
        analysisTypeE: React.PropTypes.object,
        riskAnalysisData: React.PropTypes.object,
        dim: React.PropTypes.object,
        full_context: React.PropTypes.object,
        hazardType: React.PropTypes.shape({
            mnemonic: React.PropTypes.string,
            description: React.PropTypes.string,
            analysisTypes: React.PropTypes.arrayOf(React.PropTypes.shape({
                name: React.PropTypes.string,
                title: React.PropTypes.string,
                href: React.PropTypes.string
                }))
        })
    },
    getInitialState: function() {
        return {analysisClass: 'risk'};
    },
    getDefaultProps() {
        return {
            showHazard: false,
            getData: () => {},
            getAnalysis: () => {},
            className: "col-sm-6"
        };
    },
    getRandomColor() {
        const letters = '0123456789ABCDEF';
        let color = '#';
        for (let i = 0; i < 6; i++ ) {
            color += letters[Math.floor(Math.random() * 16)];
        }
        return color;
    },
    getChartData(data, val) {
        const {dim} = this.props;
        const nameIdx = dim === 0 ? 1 : 0;
        return data.filter((d) => d[nameIdx] === val ).map((v) => {return {"name": v[dim], "value": parseInt(v[2], 10)}; });
    },    
    renderAnalysisData() {        
        const {dim, full_context, analysisType, analysisTypeE} = this.props;
        const {hazardSet, data} = this.props.riskAnalysisData;             
        const tooltip = (<Tooltip id={"tooltip-back"} className="disaster">{'Back to Analysis Table'}</Tooltip>);
        const val = data.dimensions[dim.dim1].values[dim.dim1Idx];
        const header = data.dimensions[dim.dim1].name + ': ' + val;
        const description = data.dimensions[dim.dim1].layers && data.dimensions[dim.dim1].layers[val] && data.dimensions[dim.dim1].layers[val].description ? data.dimensions[dim.dim1].layers[val].description : '';
        let selectedAnalysisType = analysisType;    
        if(this.state.analysisClass == (analysisTypeE && analysisTypeE.analysisClass && analysisTypeE.analysisClass.name))            
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
                                onChange={(idx) => this.props.setDimIdx('dim1Idx', Number.parseInt(idx[0]))}
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
                    
                    {full_context.analysis_class == 'event' ? (                        
                        <div>
                            <Panel className="panel-box">
                                <h4 className="text-center">{'Historical Events Chart'}</h4>
                                <EventCountryChart/>
                            </Panel>                            
                            <Panel className="panel-box">
                                <h4 className="text-center">{'Historical Events Chart'}</h4>
                                <ScatterChart/>
                            </Panel>
                            <Panel className="panel-box">
                                <h4 className="text-center">{'Historical Events Resume'}</h4>
                                <EventTable/>
                            </Panel>
                        </div>
                    ) : (
                        <div>                            
                            <Panel className="panel-box">
                            <h4 className="text-center">{'Current ' + data.dimensions[dim.dim1].name + ' Chart'}</h4>
                            <Chart/>
                            </Panel>                                        
                            <SummaryChart/>
                        </div>
                    )}
                    
                </div>
            </div>
        );
    },
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
    },
    renderRiskAnalysis() {
        const {analysisType = {}, analysisTypeE = {}, getAnalysis} = this.props;
        let selectedAnalysisType = analysisType;            
        if(this.state.analysisClass == (analysisTypeE && analysisTypeE.analysisClass && analysisTypeE.analysisClass.name))            
            selectedAnalysisType = analysisTypeE;        
        return selectedAnalysisType.riskAnalysis.map((rs, idx) => {
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
    },
    renderAnalysisTab() {
        const {hazardType = {}, analysisType = {}, analysisTypeE = {}, getData: loadData} = this.props;
        return (hazardType.analysisTypes || []).map((type, idx) => {
            const {href, name, title, faIcon, description, analysisClass} = type;
            const active = ((name === analysisType.name && analysisClass.name == this.state.analysisClass) || (name === analysisTypeE.name && analysisClass.name == this.state.analysisClass));
            const tooltip = (<Tooltip id={"tooltip-icon-analysis-tab-" + idx} className="disaster">{description}</Tooltip>);
            if(analysisClass.name == this.state.analysisClass) {
                return (                                
                    <OverlayTrigger key={name} placement="bottom" overlay={tooltip}>
                        <li className={`text-center ${active ? 'active' : ''}`} onClick={() => loadData(href, true)}>
                            <a href="#" data-toggle="tab"><span> <i className={"fa fa-" + faIcon}></i>&nbsp;{title}</span></a>
                        </li>
                    </OverlayTrigger>                
                );
            }
            return null;
        });
    },
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
                const active = item.name == this.state.analysisClass;                     
                return (
                    <li className={`text-center ${active ? 'active' : ''}`} onClick={() => this.selectAnalysisClass(item.name)}>
                        <a href="#" data-toggle="tab"><span>{item.title}</span></a>
                    </li>
                );
            }
            return null;
        });
    },
    selectAnalysisClass(name) {
        this.setState({analysisClass: name});
    },
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
    },
    render() {
        const {showHazard, getData: loadData} = this.props;
        return showHazard ? this.renderHazard() : (<Overview className={this.props.className} getData={loadData}/>);
    }
});

module.exports = connect(dataContainerSelector, {getAnalysis: getAnalysisData, getData, setDimIdx, setEventIdx})(DataContainer);
