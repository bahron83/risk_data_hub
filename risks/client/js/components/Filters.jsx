import React, { Component } from 'react';
import { Panel } from 'react-bootstrap';
import { connect } from 'react-redux';
import ResultList from '../components/ResultList';
const GetAnalysisBtn = connect(({disaster}) => ({loading: disaster.loading || false}))(require('../components/LoadingBtn'));


class Filters extends Component {
    constructor(props) {
        super(props);        
        this.state = {
            ht: null,
            ac: null,
            at: null            
        }; 
        this.onHazardChanged = this.onHazardChanged.bind(this);
        this.onAnalysisClassChanged = this.onAnalysisClassChanged.bind(this);
        this.onAnalysisTypeChanged = this.onAnalysisTypeChanged.bind(this);
        this.handleClick = this.handleClick.bind(this);
        this.removeFilter = this.removeFilter.bind(this);
        this.resetFilters = this.resetFilters.bind(this);        
        this.closeFilters = this.closeFilters.bind(this);        
    }

    onHazardChanged(e) {
        this.setState({
            ht: e.target.value
        })
    }

    onAnalysisClassChanged(e) {
        this.setState({
            ac: e.target.value
        })
    }

    onAnalysisTypeChanged(e) {
        this.setState({
            at: e.target.value
        })
    }    
    
    renderHazardFilter(hazardType) {        
        if(hazardType && hazardType.length > 0) {            
            return hazardType.map(h => {
                return (
                    <label key={h.mnemonic} className="label-container">{h.title}
                        <input type="radio" name="hazard" value={h.mnemonic} checked={this.state.ht === h.mnemonic} onChange={this.onHazardChanged}/>  
                        <span className="checkmark"></span>                      
                    </label>
                )                    
            })
        }
    }

    renderAnalysisClassFilter(analysisClass) {
        if(analysisClass && analysisClass.length > 0) {
            return analysisClass.map(h => {
                return (
                    <label key={h.name} className="label-container">{h.title}                        
                        <input type="radio" name="analysisClass" value={h.name} checked={this.state.ac === h.name} onChange={this.onAnalysisClassChanged}/>
                        <span className="checkmark"></span>                                              
                    </label>
                )
            })
        }
    }

    renderAnalysisTypeFilter(analysisType) {
        if(analysisType && analysisType.length > 0) {
            return analysisType.map(h => {
                return (
                    <label key={h.name} className="label-container">{h.title}                        
                        <input type="radio" name="analysisType" value={h.name} checked={this.state.at === h.name} onChange={this.onAnalysisTypeChanged}/>                        
                        <span className="checkmark"></span>                                              
                    </label>
                )
            })
        }
    }

    removeFilter(key) {
        let newState = this.state;
        newState[key] = null;
        this.setState(newState);
    }

    resetFilters() {
        this.setState({
            ht: null,
            ac: null,
            at: null
        });
    }

    renderActiveFilters() {        
        return Object.keys(this.state).map( key => {
            if(this.state[key] != null) {
                return (
                    <li key={key} className="list-group-item">{`${key}: ${this.state[key]}`}<i className="fa fa-times" onClick={() => this.removeFilter(key)}></i></li>
                )
            }            
        })        
    }

    handleClick() {
        const { applyFilters, activeFilters } = this.props;
        const { hazardType } = this.props && this.props.data;        
        if(hazardType.length > 0) {            
            const regMatch = hazardType[0]['href'].match(/reg\/(\w+)\//g);
            const locMatch = hazardType[0]['href'].match(/loc\/(\w+)\//g);
            const reg = regMatch ? regMatch[0].replace(/reg\/(\w+)\//, "$1") : null;
            const loc = activeFilters && activeFilters.loc || locMatch ? locMatch[0].replace(/loc\/(\w+)\//, "$1") : null;
            applyFilters(reg, loc, this.state.ht, this.state.ac, this.state.at);
        }        
    }    
    
    closeFilters() {
        const { toggleFiltersVisibility } = this.props;        
        toggleFiltersVisibility();
    }

    render() {
        const { switchContext, filteredAnalysis } = this.props;
        const { hazardType, analysisClass, analysisType } = this.props && this.props.data;        
        /*return (
            <div id="disaster-overview-list" className="disaster-level-container">                
                <h3 className="heading">Explore Datasets</h3>
                <Panel className="panel-box">
                    <h4>Hazard</h4>
                    {this.renderHazardFilter(hazardType)}
                </Panel>
                <Panel className="panel-box">
                    <h4>Scope</h4>
                    {this.renderAnalysisClassFilter(analysisClass)}
                </Panel>
                <Panel className="panel-box">
                    <h4>Analysis Type</h4>
                    {this.renderAnalysisTypeFilter(analysisType)}
                </Panel>
                <GetAnalysisBtn iconClass="fa fa-filter" label="Apply Filters" onClick={this.handleClick}></GetAnalysisBtn> 
                <button className="btn btn-default pull-right" onClick={this.resetFilters}>Reset Filters</button>
            </div>
        )*/
        /*<span className="close-item" onClick={this.closeFilters}><i className="fa fa-times"></i></span>*/
        return (
            <Panel id="disaster-filters-container" className="panel-box">                
                <div className="filters">
                    <h2 className="heading">Explore Datasets</h2>
                    <div>
                        <h3>Hazard</h3>
                        {this.renderHazardFilter(hazardType)}                        
                    </div>
                    <div>
                        <h3>Scope</h3>
                        {this.renderAnalysisClassFilter(analysisClass)}                        
                    </div>
                    <div>
                        <h3>Analysis Type</h3>
                        {this.renderAnalysisTypeFilter(analysisType)}
                    </div>                    
                    <button className="btn btn-default" onClick={this.handleClick}><i className="fa fa-search"></i>Apply Filters</button>
                    <button className="btn btn-default" onClick={this.resetFilters}><i className="fa fa-eraser"></i>Reset Filters</button>
                </div>                
                <ResultList switchContext={switchContext} filteredAnalysis={filteredAnalysis}/>
            </Panel>            
        )        
    }
}

export default Filters;