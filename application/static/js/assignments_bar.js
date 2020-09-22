import React, { Component } from 'react';

export default class Assignments extends Component {
  intervalID;

  state = {
    data: [],
  }

  componentDidMount() {
    this.getData();
  }

  componentWillUnmount() {
    /*
      stop getData() from continuing to run even
      after unmounting this component. Notice we are calling
      'clearTimeout()` here rather than `clearInterval()` as
      in the previous example.
    */
    clearTimeout(this.intervalID);
  }

  getData = () => {
    console.log('getting data')
    fetch('/get_assignments')
      .then(response => response.json())
      .then(data => {
        this.setState({ data: [...data] });
        // call getData() again in 5 seconds
        this.intervalID = setTimeout(this.getData.bind(this), 5000);
      });
  }

  render() {
    return (
      <div>
        Our fancy dashboard lives here.
      </div>
    );
  }
}
