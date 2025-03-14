<!-- This should be the location of the title of the repository, normally the short name -->
# IBM PowerVC Collection

<!-- Build Status, is a great thing to have at the top of your repository, it shows that you take your CI/CD as first class citizens -->
<!-- [![Build Status](https://travis-ci.org/jjasghar/ibm-cloud-cli.svg?branch=master)](https://travis-ci.org/jjasghar/ibm-cloud-cli) -->

<!-- Not always needed, but a scope helps the user understand in a short sentence like below, why this repo exists -->
## Scope

The **IBM PowerVC collection** provides modules that can be used to manage configurations
of Power systems managed by the **Power VC**.
The collection is built using the inputs from the openstack.cloud Ansible collection modules.

The collection content helps in performing the automation strategy through the Ansible ecosystem.
The IBM Power VC collection is included as an upstream collection under the Ansible
Content for IBM Power Systems umbrella of community content.
This will help 3rd party integrators and enterprises using their own automation for
Orchestration to integrate with latest versions of PowerVC quicker.

The **IBM PowerVC collection** is included as an upstream collection under the
**Ansible Content for IBM PowerVC** umbrella of community content.

<!-- A more detailed Usage or detailed explanation of the repository here -->
## Usage

This repository contains some example best practices for open source repositories:

* [LICENSE](LICENSE)
* [README.md](README.md)
* [CONTRIBUTING.md](CONTRIBUTING.md)
* [MAINTAINERS.md](MAINTAINERS.md)
* [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md) for more details you should [read this][coc].

<!-- The following are OPTIONAL, but strongly suggested to have in your repository. -->
* [travis.yml](.travis.yml) - Look https://docs.travis-ci.com/user/tutorial/ for more details.


<!-- A notes section is useful for anything that isn't covered in the Usage or Scope. Like what we have below. -->
<!-- ## Notes -->
## Requirements

### Platforms

- PowerVC

### Ansible

- Requires Ansible 2.14.0 or newer
- For help installing Ansible, refer to the [Installing Ansible] section of the Ansible Documentation
- For help installing the ibm.powervc collection, refer to the [install](docs/source/installation.rst) page of this project

### Python

- Requires Python 3.8 or higher
- openstacksdk
## Resources

Documentation of modules is generated on [GitHub Pages][pages].

## Question, Issue or Contribute

<!-- Questions can be useful but optional, this gives you a place to say, "This is how to contact this project maintainers or create PRs -->
If you have any questions or issues you can create a new [issue here][issues].

Pull requests are very welcome! Make sure your patches are well tested.
Ideally create a topic branch for every separate change you make. For
example:

1. Fork the repo
2. Create your feature branch (`git checkout -b my-new-feature`)
3. Commit your changes (`git commit -am 'Added some feature'`)
4. Push to the branch (`git push origin my-new-feature`)
5. Create new Pull Request

<!-- License and Authors is optional here, but gives you the ability to highlight who is involed in the project -->
## License & Authors

If you would like to see the detailed LICENSE click [here](LICENSE).

```text
Copyright:: 2020- IBM, Inc
This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.
This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.
You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
```

Authors:
- Karteesh Kumar Vipparapelli (karteesh.kumar.vipparapelli@partner.ibm.com)


[coc]: https://help.github.com/en/github/building-a-strong-community/adding-a-code-of-conduct-to-your-project
[issues]: https://github.com/IBM/ansible-powervc/issues/new
[pages]: https://ibm.github.io/ansible-powervc/
[Installing Ansible]: https://docs.ansible.com/ansible/latest/installation_guide/intro_installation.html
