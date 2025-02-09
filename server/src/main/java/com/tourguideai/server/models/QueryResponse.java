package com.tourguideai.server.models;

public class QueryResponse {
    private String answer;

    public QueryResponse() {
    }

    public QueryResponse(String answer) {
        this.answer = answer;
    }

    public String getAnswer() {
        return answer;
    }

    public void setAnswer(String answer) {
        this.answer = answer;
    }
}
