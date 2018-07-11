import React, { Component } from 'react';
import { connect } from 'react-redux';
import { toggleEventDetailVisibility } from '../actions/disaster';
import { eventDetailsSelector } from '../selectors/disaster';
import { Button, Modal, Panel } from 'react-bootstrap';
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
            const val = dimensions[dim.dim1].values[dim.dim1Idx];
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
    
    renderAdministrativeData(data, event) {        
        return Object.keys(data).map( key => {
            const { unitOfMeasure, values } = data[key];
            console.log(values);
            const nuts3List = event.nuts3.split(';');            
            let sumOfNuts3Values = 0;
            nuts3List.map(v => {
                sumOfNuts3Values += this.formatNumber(values[v])
            })            
            
            return (
                <ul className="list-group">
                    <li key={`${key}-country`} className="list-group-item"><label>{key} of Country</label>{`${this.formatNumber(values[event.iso2])} (${unitOfMeasure})`}</li>
                    <li key={`${key}-nuts`} className="list-group-item"><label>{key} of nuts3 affected</label>{`${sumOfNuts3Values} (${unitOfMeasure})`}</li>
                </ul>
            )
        });
    }
    
    render() {   
        const { eventDetails, showEventDetail, visibleEventDetail, riskAnalysisData, toggleEventDetailVisibility } = this.props;
        const { data, overview } = eventDetails;
        const { event } = overview || {};
        const { administrativeData } = overview || {};        
        const showToggle = riskAnalysisData && riskAnalysisData.events ? true : false;
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
                            
                            {this.renderAdministrativeData(administrativeData, event)} 
                            
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