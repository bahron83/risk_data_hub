import React, { Component } from 'react';
import { connect } from 'react-redux';
import { toggleEventDetailVisibility } from '../actions/disaster';
import { eventDetailsSelector } from '../selectors/disaster';
import { Button, Modal, Panel } from 'react-bootstrap';
import _ from 'lodash';
import Chart from './Chart';


class EventDetails extends Component {  
    constructor(props) {
        super(props);
        this.state = { 
            isOpen: true            
        };
    }
    
    renderChart(data) {          
        const { dim } = this.props;          
        return Object.keys(data).map( key => {
            const { values, dimensions, eventAnalysis } = data[key];            
            const currentDimension = dimensions[dim.dim1Idx];
            const val = currentDimension.charAt(0).toUpperCase() + currentDimension.substr(1);            
            const { unit_of_measure: unitOfMeasure } = eventAnalysis;
            return (
                <Panel key={val} className="panel-box">
                    <h5>{val}</h5>
                    <Chart dim={dim} values={values} val={val} dimension={dimensions} uOm={unitOfMeasure} selectRP={function(){}}/>
                </Panel>
            )
        });        
    } 

    formatNumber(string) {
        return Math.round(parseFloat(string) * 100) / 100        
    }
    
    round(value, decimals = null) {
        if(!decimals)
            decimals = this.props && this.props.riskAnalysisData && this.props.riskAnalysisData.decimalPoints || 3;        
        const adjustedValue = value.toString().indexOf('e') > -1 ? value : value+'e'+decimals;        
        return Number(Math.round(adjustedValue)+'e-'+decimals);
    }

    computeAdminDataAggregation(adminLevel, event, values) {
        let res = 0;
        const admList = event[adminLevel].split(',');

        if(admList.length > 0) {            
            for(let k in admList) {
                if(values[admList[k]])
                    res += values[admList[k]]['value'];
            } 
                
        }                
        return res;
    }

    computeAdmindataDimension(adminLevel, event, values) {
        const admList = event[adminLevel].split(',');
        if(admList.length > 0) {
            if(values[admList[0]])
                return values[admList[0]]['dimension'];        
        }
        return null;
    }
    
    renderAdministrativeData(overview, dataSource) {          
        const { administrativeData, event, threshold } = overview;             
        return Object.keys(administrativeData).map(key => {               
            const { unitOfMeasure, values, ratios } = administrativeData[key];            
            const countryAdminData = this.computeAdminDataAggregation('iso2', event, values);            
            const countryAdminDataDim = this.computeAdmindataDimension('iso2', event, values);            
            const eventByCountry = ratios && ratios.country && ratios.country[dataSource] * 100;            
            const nuts2AdminData = this.computeAdminDataAggregation('nuts2', event, values);
            const nuts2AdminDataDim = this.computeAdmindataDimension('nuts2', event, values);
            const eventByNuts2 = ratios && ratios.nuts2 && ratios.nuts2[dataSource] * 100;
            const nuts3AdminData = this.computeAdminDataAggregation('nuts3', event, values);
            const nuts3AdminDataDim = this.computeAdmindataDimension('nuts3', event, values);
            const eventByNuts3 = ratios && ratios.nuts3 && ratios.nuts3[dataSource] * 100;
            
            //const { unitOfMeasure, countryAdminData, nuts2AdminData, nuts3AdminData, countryAdminDataDim, nuts2AdminDataDim, nuts3AdminDataDim, eventByCountry, eventByNuts2, eventByNuts3, threshold } = dataProcessed[key];            
            const cssClass = key == 'GDP' ? this.isEligibleForEUSF(overview, dataSource) ? 'outset eligible' : 'outset not-eligible' : '';
            return (
                <ul key={key} className="list-group">
                    <li key={`${key}-country`} className="list-group-item">
                        <label>{key} of Country</label>
                        {`${countryAdminData.toLocaleString()} ${unitOfMeasure} (${countryAdminDataDim})`}
                        <span className={`right ${eventByCountry > threshold ? 'eligible' : 'not-eligible'}`}>{eventByCountry ? `${this.round(eventByCountry, 3)} %` : ''}</span>
                    </li>
                    <li key={`${key}-nuts2`} className={`list-group-item ${cssClass}`}>
                        <label>{key} of NUTS2 affected</label>
                        {`${nuts2AdminData.toLocaleString()} ${unitOfMeasure} (${nuts2AdminDataDim})`}
                        <span className={`right ${eventByNuts2 > threshold ? 'eligible' : 'not-eligible'}`}>{eventByNuts2 ? `${this.round(eventByNuts2, 3)} %` : ''}</span>
                        {this.renderGDPText(overview, dataSource, key)}
                    </li>
                    <li key={`${key}-nuts3`} className="list-group-item">
                        <label>{key} of NUTS3 affected</label>
                        {`${nuts3AdminData.toLocaleString()} ${unitOfMeasure} (${nuts3AdminDataDim})`}
                        <span className={`right ${eventByNuts3 > threshold ? 'eligible' : 'not-eligible'}`}>{eventByNuts3 ? `${this.round(eventByNuts3, 3)} %` : ''}</span>
                    </li>
                </ul>
            )
        });
    }    

    processAdministrativeData(overview, data) {
        const { administrativeData, damageAssessmentMapping, event, threshold } = overview || {}; 
        let dataProcessed = {};
        Object.keys(administrativeData).map(key => {            
            const { unitOfMeasure, values } = administrativeData[key];                 
            if(event.iso2 in values) {
                const nuts3List = event.nuts3.split(';');                              
                const eventAdminData = data[damageAssessmentMapping[key]] && data[damageAssessmentMapping[key]]["values"] && data[damageAssessmentMapping[key]]["values"][0] && this.round(data[damageAssessmentMapping[key]]["values"][0][2]);                
                const countryAdminData = this.round(values[event.iso2]['value']);            
                const countryAdminDataDim = values[event.iso2]['dimension'];  
                let nuts2AdminData = 0;   
                let nuts2AdminDataDim = null;                      
                let nuts3AdminData = 0;
                let nuts3AdminDataDim = null;
                _.forOwn(_.omit(values, event.iso2), (v, k) => {
                    const formattedValue = this.round(v['value']);
                    nuts2AdminData += formattedValue;                
                    nuts2AdminDataDim = v['dimension'];
                    if(nuts3List.includes(k)) {
                        nuts3AdminData += formattedValue;
                        nuts3AdminDataDim = v['dimension'];
                    }                    
                });
                
                const eventByCountry = eventAdminData ? this.round(eventAdminData / countryAdminData * 100) : null;
                const eventByNuts2 = eventAdminData ? this.round(eventAdminData / nuts2AdminData * 100) : null;
                const eventByNuts3 = eventAdminData ? this.round(eventAdminData / nuts3AdminData * 100) : null;

                dataProcessed[key] = {
                    'unitOfMeasure': unitOfMeasure,
                    'countryAdminData': countryAdminData,
                    'nuts2AdminData': nuts2AdminData,
                    'nuts3AdminData': nuts3AdminData,
                    'eventByCountry': eventByCountry,
                    'eventByNuts2': eventByNuts2,
                    'eventByNuts3': eventByNuts3,
                    'countryAdminDataDim': countryAdminDataDim,
                    'nuts2AdminDataDim': nuts2AdminDataDim,
                    'nuts3AdminDataDim': nuts3AdminDataDim,
                    'threshold': threshold
                }
                
            }            
        });
        return dataProcessed;        
    }
    
    renderGDPText(overview, dataSource, key) {
        if(key == 'GDP') {
            const { threshold } = overview;
            if(this.isEligibleForEUSF(overview, dataSource)) 
                return (                    
                    <p>{`Economic losses exceed ${threshold}% of the GDP in regions (NUTS2) affected`}</p>                                            
                )            
            else 
                return (                    
                    <p>{`Economic losses DO NOT exceed ${threshold}% of the GDP in regions (NUTS2) affected or there is no data available`}</p>                                            
                )            
        }
        return null;
    }
    
    renderEligibleText(overview, dataSource) {        
        if(this.isEligibleForEUSF(overview, dataSource))             
            return (                
                <p className="bigtext eligible">This event appears to be eligible for EU Solidarity Funds</p>                
            )
        else 
            return (            
                <p className="bigtext not-eligible">This event DOES NOT appear to be eligible for EU Solidarity Funds</p>            
        )
    }  
    
    isEligibleForEUSF(overview, dataSource) {        
        return overview.isEligibleForEUSF && overview.isEligibleForEUSF[dataSource] || false;
    }
    
    render() {   
        const { eventDetails, showEventDetail, visibleEventDetail, toggleEventDetailVisibility } = this.props;
        const { data, overview, dataSources } = eventDetails;        
        const { event } = overview || {}; 
        const defaultDataSource = dataSources && dataSources[0];
        const dataSource = defaultDataSource;                
        if(data && showEventDetail) {            
            return (            
                <div>
                    <Modal show={visibleEventDetail} onHide={toggleEventDetailVisibility}>
                        <Modal.Header closeButton>
                            <Modal.Title>Event Detail Analysis</Modal.Title>
                        </Modal.Header>
                        <Modal.Body>                                                        
                            <ul className="list-group">
                                <li className="list-group-item"><label>Event Code</label>{event.code}</li>
                                <li className="list-group-item"><label>Hazard Type</label>{event.hazard_title}</li>
                                <li className="list-group-item"><label>Country</label>{event.iso2}</li>
                                <li className="list-group-item"><label>NUTS2 affected</label>{event.nuts2_names}</li>
                                <li className="list-group-item"><label>NUTS3 affected</label>{event.nuts3_names}</li>
                                <li className="list-group-item"><label>Begin Date</label>{event.begin_date}</li>
                                <li className="list-group-item"><label>End Date</label>{event.end_date}</li>
                                <li className="list-group-item"><label>Event Source</label>{event.event_source}</li>
                                <li className="list-group-item"><label>Cause</label>{event.cause}</li>
                                <li className="list-group-item"><label>Notes</label>{event.notes}</li>
                                <li className="list-group-item"><label>Sources</label>{event.sources}</li>                        
                            </ul>
                            <hr />
                            <h4>EU Solidarity funds</h4>
                            {this.renderEligibleText(overview, dataSource)}                            
                            <hr />
                            <h4>Administrative data for country</h4>
                            <p>Census data from Eurostat and percentage value of the event</p>
                            {this.renderAdministrativeData(overview, dataSource)}                                                                                     
    
                            <hr />
                            <h4>Comparison Charts</h4>
                            <p>Impact of the event vs potential impact based on models (per return period expressed in years)</p>
                            {this.renderChart(data)}
                        </Modal.Body>
                        <Modal.Footer>
                            <Button onClick={toggleEventDetailVisibility}>Close</Button>
                        </Modal.Footer>
                    </Modal>                    
                </div>            
            );
        }
        return null;
    }
}

export default connect(eventDetailsSelector, {toggleEventDetailVisibility})(EventDetails);