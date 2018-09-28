import React, { Component } from 'react';
import { connect } from 'react-redux';
import { admDivisionLookup, getAnalysisData, switchContext } from '../actions/disaster';
import { lookupResultsSelector } from '../selectors/disaster';


class Search extends Component {
    constructor(props) {
        super(props);        
        this.state = {
            term: this.props.value || '',
            throttle: this.props.throttle || 200            
        };
        this.updateSearch = this.updateSearch.bind(this);
        this.handleClick = this.handleClick.bind(this);          
        this.loadAnalysis = this.loadAnalysis.bind(this);          
    }
    
    updateSearch(e) {   
        const { contextUrl, admDivisionLookup } = this.props;
        this.setState({term: e.target.value}, () => {            
            if(String(this.state.term).length > 3) {            
                //call api                
                admDivisionLookup(`${contextUrl}/risks/data_extraction/admlookup/${this.state.term}/`);
            }
        });        
        
    }

    handleClick(item) {        
        const { admDivisionLookup, contextUrl, region } = this.props;  
        if(item.admCode)              
            admDivisionLookup(`${contextUrl}/risks/data_extraction/reg/${region}/loc/${item.admCode}/detail/yes/`, true);
    }

    renderResultList() {
        const { lookupResults, lookupResultsDetail } = this.props;         
        if(this.state.term != '') {
            if(lookupResultsDetail.length > 0)
                return this.renderPreviewBox();
            else if (lookupResults.length > 0) {
                return (
                    <div className="autocomplete-box">
                        <ul className="list-group lookup-res lookup-res-main">
                        {lookupResults.map(r => {
                            const rowText = r.admCode ? `${r.admName} (${r.admCode} - Country: ${r.countryName})` : 'No results found';
                            return <li className="list-group-item" key={r.admCode} onClick={() => this.handleClick(r)}>{rowText}</li>
                        })}
                        </ul>
                    </div>       
                )
            }
        }        
        return null;
    }

    renderPreviewBox() {
        const { lookupResultsDetail } = this.props;
        if (lookupResultsDetail.length > 0) {
            return (
                <div className="autocomplete-box">
                    <h4>Available analysis</h4>
                    <ul className="list-group lookup-res lookup-res-group">
                    {lookupResultsDetail.map(r => {
                        return (
                            <li key={r.riskAnalysis.id} className="list-group-item" onClick={() => this.loadAnalysis(r)}>
                                <ul className="list-group lookup-res lookup-res-detail">
                                    <label>Hazard type:</label><li key={`${r.riskAnalysis.id}${r.hazardType}`} className="list-group-item">{r.hazardType}</li>
                                    <label>Analysis type:</label><li key={`${r.riskAnalysis.id}${r.analysisType}`} className="list-group-item">{r.analysisType}</li>
                                    <label>Analysis name:</label><li key={`${r.riskAnalysis.id}${r.riskAnalysis.name}`} className="list-group-item">{r.riskAnalysis.name}</li>
                                    <label>Available at level:</label><li key={`${r.riskAnalysis.id}${r.admName}`} className="list-group-item">{r.admName}</li>
                                </ul>
                            </li>)
                    })}
                    </ul>
                </div>       
            )
        }
        return null;
    }    
    
    loadAnalysis(item) {
        const { switchContext } = this.props; 
        const { ht, at, an, reg, loc } = item && item.context;       
        this.setState({term: ''}, () => switchContext(ht, at, an, reg, loc));        
    }

    resetComponent() {        
        this.refs.searchTerm.value = '';
        this.setState({term: ''});        
    }
    
    renderResetItem() {
        if(this.state.term != '')
            return (
                <span className="lookup-reset-item" onClick={() => this.resetComponent()}><i className="fa fa-times"></i></span>
            )
        return null;
    }

    render() {        
        return (
            <div className="form-group">
                
                <input type="text" className="form-control" placeholder="Search location" value={this.state.term} ref="searchTerm" onChange={this.updateSearch} />
                {this.renderResetItem()}
                {this.renderResultList()}                
            </div>         
        );
    }   

}

export default connect(lookupResultsSelector, { admDivisionLookup, switchContext })(Search);