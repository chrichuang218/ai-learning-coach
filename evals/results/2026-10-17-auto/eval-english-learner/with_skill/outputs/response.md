Let’s use **go-chi/chi**, a Go web router. It gives us a concrete behavior to investigate while using your Python experience with functions and control flow as a starting point.

The starter track points to [`tree.go` at a pinned commit](https://github.com/go-chi/chi/blob/3a33ba578e0dd93444e0ff386cc26e665d92e31e/tree.go), starting with `(*node).findRoute`. I haven’t inspected that source or run it here, so its behavior is still something to verify.

Start with one prediction: suppose a router has `/users/{id}`, where `{id}` represents a variable path segment, and `/users/me`. For a request to `/users/me`, **which route would you expect to match, and why?** No Go syntax is needed yet.

### File or tool writes

None at this stage. I would keep this first exchange in the conversation without creating a Learning Lab, recording mastery, or updating progress. Source verification would come before teaching implementation details or registering the project as verified.
