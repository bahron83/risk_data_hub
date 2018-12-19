import React, { Component } from 'react';
import { connect } from 'react-redux';
import { Panel, Tooltip, OverlayTrigger } from 'react-bootstrap';
const GetAnalysisBtn = connect(({disaster}) => ({loading: disaster.loading || false}))(require('../components/LoadingBtn'));


class ResultList extends Component { 
    renderRiskAnalysisHeader(title, idx, locationName) {
        const tooltip = (<Tooltip id={"tooltip-abstract-" + idx} className="disaster">{'Show Abstract'}</Tooltip>);
        return (
          <OverlayTrigger placement="top" overlay={tooltip}>          
            <div className="row">
                <div className="col-xs-10">
                    <div className="disaster-analysis-title">{title}</div>
                    <div className="disaster-analysis-loc"><i className="icon-pin"></i>{locationName}</div>
                </div>
                <div className="col-xs-2">
                    <i className="pull-right fa fa-chevron-down"></i>
                </div>          
            </div>            
          </OverlayTrigger>
        );
    }
    
    renderList(filteredAnalysis) {
        return filteredAnalysis.map((rs, idx) => {
            /*const an = rs['riskAnalysis'];
            const ht = rs['hazardType'];
            const at = rs['analysisType'];
            const loc = rs['location'];
            return (
                <tr key={an.name} className="table-row" onClick={() => this.loadAnalysis(v)}>
                    <th scope="col" className="table-cell">{ht.title}</th>
                    <th scope="col" className="table-cell">{at.title}</th>
                    <th scope="col" className="table-cell">{an.name}</th>
                    <th scope="col" className="table-cell">{loc.label}</th>
                </tr>
            )*/
            const { title, fa_icon: faIcon, abstract } = rs.riskAnalysis.hazardSet;
            const { label: locationName } = rs.location;
            const tooltip = (<Tooltip id={"tooltip-icon-cat-" + idx} className="disaster">{'Analysis Data'}</Tooltip>);
            return (
                <div key={idx} className="row">
                    <div className="col-xs-1 text-center">
                        <OverlayTrigger placement="bottom" overlay={tooltip}>
                        <i className={'disaster-category fa ' + faIcon} onClick={()=> this.loadAnalysis(rs)}></i>
                        </OverlayTrigger>
                    </div>
                    <div className="col-xs-11">
                        <Panel collapsible header={this.renderRiskAnalysisHeader(title, idx, locationName)}>
                            {abstract}
                            <br/>
                            <GetAnalysisBtn onClick={()=> this.loadAnalysis(rs)}
                            iconClass="fa fa-bar-chart" label="Analysis Data"/>
                        </Panel>
                    </div>                
                </div>                
            )
        })
    }

    loadAnalysis(item) {
        const { switchContext } = this.props;         
        const { ht, at, an, reg, loc } = item && item.context;          
        this.setState({term: ''}, () => switchContext(ht, at, an, reg, loc));        
    }
    
    render() {   
        const { filteredAnalysis } = this.props;          
        return (
            <div id="disaster-filter-results" className="disaster-analysis">                    
                {filteredAnalysis ? (
                    filteredAnalysis.length > 0 ? (                        
                        this.renderList(filteredAnalysis)                        
                    ) : <span className="no-results">No data matches the specified criteria.</span>
                ) : null}                
            </div>                
        )                    
    }
}

export default ResultList;