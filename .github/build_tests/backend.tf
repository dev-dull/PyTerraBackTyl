terraform {
  backend "http" {
    address = "http://localhost:2442/?env=InT"
    lock_address = "http://localhost:2442/lock?env=InT"
    unlock_address = "http://localhost:2442/unlock?env=InT"
    skip_cert_verification = "true"
  }
}