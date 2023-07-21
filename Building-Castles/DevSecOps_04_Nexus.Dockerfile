FROM busybox

ENV NCAT_MESSAGE "Container test"
ENV NCAT_HEADER "HTTP/1.1 200 OK"
ENV NCAT_PORT "8888"

RUN addgroup -S nonroot && \                                                 
    adduser -S nonroot -G nonroot                                            
                                                                                
USER nonroot

CMD /bin/nc -l -k -p ${NCAT_PORT} -e /bin/echo -e "${NCAT_HEADER}\n\n${NCAT_MESSAGE}"
