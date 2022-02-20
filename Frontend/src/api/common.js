export function send_json_request(endpoint, method, data, on_success, on_fail) {
    const url = endpoint
    let payload = JSON.stringify(data)
    let xhr = new XMLHttpRequest()
    xhr.open(method, url, true)
    xhr.setRequestHeader("Content-Type", "application/json")
    xhr.send(payload)

    xhr.onreadystatechange = function() {
        if(this.status === 200) {
            console.log(this.responseText)
            on_success(JSON.parse(this.responseText))
        }
        else if(this.status >= 300)
            on_fail(this.response)
    }
}