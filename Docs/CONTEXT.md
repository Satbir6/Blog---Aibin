# Blog Website Specification

This document outlines the flow, structure, and features of a blog website that allows users to read blogs and create their own. It is intended to guide a web developer in understanding the requirements and how each part of the site should function.

---

## Tech Stack:
- **Frontend**:
  - **HTML, CSS, JavaScript** for structure and interactivity.
  - **AJAX** for asynchronous data fetching to enhance user experience.
- **UI Framework**:
  - **Tailwind CSS** for utility-first styling.
  - **Flowbite** for prebuilt, accessible UI components.
- **Backend**:
  - **Flask (Python)** for server-side logic, routing, and data processing.
- **Database**:
  - **SQLite** for a lightweight, file-based relational database solution.


## 1. Homepage

### 1.1 Header Section
- **Logo** (top-left corner)
  - Acts as a link to the homepage.
- **Navigation Bar** (top-right or below the logo)
  - Contains primary navigation links. 
  - Visibility changes depending on whether the user is logged in or not.
- **Search Bar** (centrally placed or within the header)
  - Allows users to search for blog posts by keywords.
- **Call-to-action (CTA) Buttons**: 
  - **Sign Up** or **Log In** (visible when logged out).

### 1.2 Blog Categories Section
- Displays **cards** or **tiles** for different categories (e.g., *Technology*, *Lifestyle*, *Travel*).
- Each category link directs to a category-specific blog list page.

### 1.3 Recent Blogs Section
- Shows a list of recently published blog posts.
  - **Information displayed**: 
    - Title
    - Author
    - Date
    - Short excerpt
    - “Read More” button (links to full blog post)
- **Pagination** or a “Load More” button at the bottom to handle large numbers of posts.

### 1.4 Footer
- Contains links to:
  - **About Us**
  - **Privacy Policy**
  - **Terms of Service**

---

## 2. Navigation Bar (Navbar)

### 2.1 Logged-Out State
- **Home**
- **Categories** (can be a dropdown or expandable menu)
- **About Us**
- **Sign Up** / **Log In**
  - Takes the user to the respective pages to create an account or log into an existing one.

### 2.2 Logged-In State
- **Home**
- **Categories**
- **About Us**
- **Contact**
- **Profile** (dropdown menu)
  - **My Account** (goes to the profile page)
  - **My Blogs** (lists all blogs created by the user)
  - **Log Out** (ends the session and returns to the logged-out state)

### 2.3 Search Bar
- Appears in both logged-in and logged-out states.
- On submission, redirects to a **Search Results** page displaying matching blogs.

---

## 3. Blog Display

### 3.1 Blog List Page
- **Layout**:
  - Grid or list format.
- **Each blog preview includes**:
  - Title
  - Author name
  - Publish date
  - Short excerpt (summary or introduction)
  - **Read More** button (links to the single blog page)
- **Filters/Sorting**:
  - By date (newest to oldest or vice versa)
  - By popularity (e.g., number of views or likes)
  - By category
- **Pagination** or “Load More” functionality for extensive lists.

### 3.2 Single Blog Page
- **Content**:
  - Full blog title
  - Author details (name)
  - Publish date
  - Body text (full content)
- **Social Sharing Buttons**:
  - Allows users to share the blog on social media platforms.
- **Comments Section**:
  - Visible to all, but only logged-in users can comment.
  - Nested or threaded comments (optional).
- **Related Blogs Section**:
  - At the bottom, displaying similar or recommended blog posts.

---

## 4. Account Section

### 4.1 Logged-Out State

#### 4.1.1 Sign Up Page
- **Form Fields**:
  - Name
  - Email
  - Password
  - Confirm Password
- **Link** to the **Log In** page for existing users.

#### 4.1.2 Log In Page
- **Form Fields**:
  - Email
  - Password
- **Link** to the **Sign Up** page for new users.

### 4.2 Logged-In State

#### 4.2.1 Profile Page
- **User Details**:
  - Name
  - Email
- **Option to edit profile**:
  - Change name or email (if supported).
- **List of user’s published blogs**:
  - Title and date published.
  - Edit or Delete buttons for each blog (if authorised).
- **Option to create a new blog**.

#### 4.2.2 Create/Edit Blog Page
- **Form Fields**:
  - **Title**
  - **Category** (dropdown or selection)
  - **Content** (WYSIWYG editor for rich text)
- **Publish/Save Draft Buttons**:
  - Publish makes the blog publicly visible.
  - Save Draft keeps it private to the author until later publication.

#### 4.2.3 Dashboard (Optional)
- **Overview**:
  - Number of blogs created
  - Number of comments or likes
- **Quick Links**:
  - Create a new blog
  - Edit profile
  - View stats (if applicable)

---

## 5. Additional Features

### 5.1 Search Results Page
- Displays all blogs matching the search query in a layout similar to the **Blog List Page**.
- May include additional filters or sorting options relevant to search queries.

### 5.2 Category Page
- Shows blogs filtered by the selected category.
- Includes a **Category Description** at the top (optional).
- Layout similar to the **Blog List Page**.

### 5.3 404 Page
- Custom error page displayed for invalid URLs.
- Provides a link back to the **Homepage** to guide users.

---

## 6. User State Management

### 6.1 Auth Matrix

| **Action**       | **Logged-Out**    | **Logged-In**        |
|------------------|-------------------|----------------------|
| Create Blog      | Redirect to Login | Show Editor          |
| Comment          | Disabled          | Allowed              |
| Profile Access   | Sign Up CTA       | Personal Dashboard   |
| Blog Ownership   | N/A               | Edit/Delete Options  |

---

## 7. Technical Considerations
- **Responsive Design**: Ensure layouts adjust smoothly across desktop, tablet, and mobile.
- **Performance**:
  - Lazy-loading images
  - Caching frequently accessed data
- **Security**:
  - HTTPS and secure forms
  - Proper user authentication and authorisation
- **Scalability**:
  - Use pagination or infinite scroll for blog lists.
  - Efficient database queries and indexing.

---

## 8. Database Schema

Below is a suggested database schema. Depending on your tech stack and additional requirements (e.g., tags, user roles), you may need to adjust or expand these tables.

### 8.1 `users` Table
| Field          | Type           | Description                                      |
|----------------|--------------- |--------------------------------------------------|
| **id**         | INT (PK, AI)   | Unique user identifier                          |
| **name**       | VARCHAR(...)   | User’s full name                                |
| **email**      | VARCHAR(...)   | User’s email (unique)                           |
| **password**   | VARCHAR(...)   | Hashed password                                 |
| **created_at** | DATETIME       | Timestamp when the user was created             |
| **updated_at** | DATETIME       | Timestamp when the user’s data was last updated |

### 8.2 `categories` Table
| Field          | Type           | Description                                        |
|----------------|--------------- |----------------------------------------------------|
| **id**         | INT (PK, AI)   | Unique category identifier                        |
| **name**       | VARCHAR(...)   | Category name (e.g., Technology, Lifestyle)       |
| **description**| TEXT           | Optional description for the category             |
| **created_at** | DATETIME       | Timestamp when the category was created           |
| **updated_at** | DATETIME       | Timestamp when the category was last updated      |

### 8.3 `blogs` Table
| Field          | Type           | Description                                        |
|----------------|--------------- |----------------------------------------------------|
| **id**         | INT (PK, AI)   | Unique blog identifier                            |
| **title**      | VARCHAR(...)   | Title of the blog                                 |
| **content**    | TEXT           | Full content of the blog                          |
| **author_id**  | INT (FK)       | References `users(id)`                            |
| **category_id**| INT (FK)       | References `categories(id)`                       |
| **status**     | VARCHAR(...)   | e.g., ‘draft’ or ‘published’                      |
| **created_at** | DATETIME       | Timestamp when the blog was created               |
| **updated_at** | DATETIME       | Timestamp when the blog was last updated          |

### 8.4 `comments` Table
| Field          | Type           | Description                                        |
|----------------|--------------- |----------------------------------------------------|
| **id**         | INT (PK, AI)   | Unique comment identifier                         |
| **blog_id**    | INT (FK)       | References `blogs(id)`                            |
| **user_id**    | INT (FK)       | References `users(id)`                            |
| **content**    | TEXT           | The comment text                                  |
| **created_at** | DATETIME       | Timestamp when the comment was created            |
| **updated_at** | DATETIME       | Timestamp when the comment was last updated       |

### 8.5 `likes` Table
| Field          | Type           | Description                                        |
|----------------|--------------- |----------------------------------------------------|
| **id**         | INT (PK, AI)   | Unique like identifier                            |
| **blog_id**    | INT (FK)       | References `blogs(id)`                            |
| **user_id**    | INT (FK)       | References `users(id)`                            |
| **created_at** | DATETIME       | Timestamp when the like was registered            |

---

## 9. Conclusion
This specification provides a structured blueprint of the blog website, detailing the homepage layout, navigation, blog display, user account management, user state management, database schema, and additional features. By following these guidelines, developers can implement a user-friendly and maintainable platform where users can read, create, and manage their own blogs.

## 10. Folder Structure 

- **app.py**  
  All of your Flask routes, configuration, database interactions, and logic reside here.

- **templates/**  
  Contains all HTML templates.  
  - **base.html**: A universal layout (header, footer, nav) that other templates extend.  
  - **index.html**: Homepage template.  
  - **login.html**, **signup.html**, **profile.html**: Pages for user authentication and profile management.  
  - **create_blog.html**: Template for creating or editing a blog post.  
  - **single_blog.html**: Displays an individual blog post.

- **static/**  
  Houses your static assets such as CSS, JavaScript, and images.  
  - **css/**: Stylesheets. If you’re using Tailwind CSS, you might place your compiled CSS here.  
  - **js/**: JavaScript scripts.  
  - **images/**: Images, icons, and other visual assets.  

