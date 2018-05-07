import React, { Component } from 'react';

class Paginator extends Component {
    render () {
        const { total, showing } = this.props;        
        return (            
            <div>
                {this.renderButton()}
                <p>Showing: {showing} of {total} results</p>                
            </div>
        );
    }

    renderButton() {
        const { total, showing, loading } = this.props;
        return showing < total ? <button className="loadAll btn btn-default pull-right" onClick={this.handleClick.bind(this)}><i className={loading && "icon-spinner fa-spin" || 'fa fa-bar-chart'}/>Load all results</button> : null;
    }

    handleClick(e) {         
        const { fullContext, getAnalysisData } = this.props;        
        getAnalysisData(`${fullContext.full_url}load/all/`);
    }
}

export default Paginator;