# The team folder

Each team member has a YAML file in this folder. The files provide the metadata
used to render the cards on `../teams.qmd`.

## Adding a new member

1. Copy `template.yaml` and rename it to your name:

   ```sh
   cp template.yaml FirstName-LastName.yaml
   ```

2. Replace the placeholder values with your name, image, role, organization,
   biography, areas of expertise, social links, and hackathon user groups.
3. Put the image referenced by `image` in `../images/team/`.
4. Add the new YAML file to the `contents` list in `../teams.qmd`.
5. Render the hackathon book locally and open a pull request for review.
