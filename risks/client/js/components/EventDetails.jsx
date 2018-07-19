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
        this.state = { isOpen: true };
    }
    
    renderChart(data) {        
        const { dim, riskAnalysisData } = this.props;        
        return Object.keys(data).map( key => {
            const { values, dimensions } = data[key];            
            const currentDimension = dimensions[dim.dim1].values[dim.dim1Idx];
            const val = currentDimension.charAt(0).toUpperCase() + currentDimension.substr(1);
            const { unitOfMeasure } = riskAnalysisData || 'Values';
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
    
    renderAdministrativeData(overview, data) {  
        const { administrativeData, riskAnalysisMapping, event, threshold } = overview || {};          
        return Object.keys(administrativeData).map(key => {
            const { unitOfMeasure, values } = administrativeData[key];            
            const nuts3List = event.nuts3.split(';');              
            const eventAdminData = data[riskAnalysisMapping[key]] && data[riskAnalysisMapping[key]]["values"] && data[riskAnalysisMapping[key]]["values"][0] && this.formatNumber(data[riskAnalysisMapping[key]]["values"][0][2]);
            const countryAdminData = this.formatNumber(values[event.iso2]);  
            let nuts2AdminData = 0;          
            let nuts3AdminData = 0;
            _.forOwn(_.omit(values, event.iso2), (v, k) => {
                const formattedValue = this.formatNumber(v);
                nuts2AdminData += formattedValue;                
                if(nuts3List.includes(k))
                    nuts3AdminData += formattedValue;
            });
            
            const eventByCountry = eventAdminData ? this.formatNumber(eventAdminData / countryAdminData * 100) : null;
            const eventByNuts2 = eventAdminData ? this.formatNumber(eventAdminData / nuts2AdminData * 100) : null;
            const eventByNuts3 = eventAdminData ? this.formatNumber(eventAdminData / nuts3AdminData * 100) : null;
            
            return (
                <ul key={key} className="list-group">
                    <li key={`${key}-country`} className="list-group-item">
                        <label>{key} of Country</label>
                        {`${countryAdminData} (${unitOfMeasure})`}
                        <span className={`right ${eventByCountry > threshold ? 'red' : 'blue'}`}>{eventByCountry ? `${eventByCountry} %` : ''}</span>
                    </li>
                    <li key={`${key}-nuts2`} className="list-group-item">
                        <label>{key} of nuts2 affected</label>
                        {`${nuts2AdminData} (${unitOfMeasure})`}
                        <span className={`right ${eventByNuts2 > threshold ? 'red' : 'blue'}`}>{eventByNuts2 ? `${eventByNuts2} %` : ''}</span>
                    </li>
                    <li key={`${key}-nuts3`} className="list-group-item">
                        <label>{key} of nuts3 affected</label>
                        {`${nuts3AdminData} (${unitOfMeasure})`}
                        <span className={`right ${eventByNuts3 > threshold ? 'red' : 'blue'}`}>{eventByNuts3 ? `${eventByNuts3} %` : ''}</span>
                    </li>
                </ul>
            )
        });
    }
    
    render() {   
        const { eventDetails, showEventDetail, visibleEventDetail, riskAnalysisData, toggleEventDetailVisibility } = this.props;
        const { data, overview } = eventDetails;
        const { event } = overview || {};        
        //const showToggle = riskAnalysisData && riskAnalysisData.events ? true : false;
        return (
            data && showEventDetail ?                 
                <div>
                    <Modal show={visibleEventDetail} onHide={toggleEventDetailVisibility}>
                        <Modal.Header closeButton>
                            <Modal.Title>Event Detail Analysis</Modal.Title>
                        </Modal.Header>
                        <Modal.Body>
                            <ul className="list-group">
                                <li className="list-group-item"><label>Event ID</label>{event.event_id}</li>
                                <li className="list-group-item"><label>Hazard Type</label>{event.hazard_type}</li>
                                <li className="list-group-item"><label>Country</label>{event.iso2}</li>
                                <li className="list-group-item"><label>Nuts2 affected</label>{event.nuts2_names}</li>
                                <li className="list-group-item"><label>Nuts3 affected</label>{event.nuts3_names}</li>
                                <li className="list-group-item"><label>Begin Date</label>{event.begin_date}</li>
                                <li className="list-group-item"><label>End Date</label>{event.end_date}</li>
                                <li className="list-group-item"><label>Event Source</label>{event.event_source}</li>
                                <li className="list-group-item"><label>Cause</label>{event.cause}</li>
                                <li className="list-group-item"><label>Notes</label>{event.notes}</li>
                                <li className="list-group-item"><label>Sources</label>{event.sources}</li>                        
                            </ul>
                            <hr />
                            <h4>Administrative data for country</h4>
                            
                            {this.renderAdministrativeData(overview, data)} 
                            
                            <hr />
                            <h4>Comparison Charts</h4>
                            <p>Impact of the event vs potential impact based on models (per return period)</p>
                            {this.renderChart(data)}
                        </Modal.Body>
                        <Modal.Footer>
                            <Button onClick={toggleEventDetailVisibility}>Close</Button>
                        </Modal.Footer>
                    </Modal>                    
                </div>
            : null
        );
    }
}

export default connect(eventDetailsSelector, {toggleEventDetailVisibility})(EventDetails);