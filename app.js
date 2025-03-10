const express = require('express');
const cors = require('cors');
const { v4: uuidv4 } = require('uuid');
const { Server } = require('socket.io');
const http = require('http');

const app = express();
const server = http.createServer(app);

// Configure environment variables
const SECRET_KEY = process.env.SECRET_KEY || 'default-secret-key';
const CORS_ALLOWED_ORIGINS = process.env.CORS_ALLOWED_ORIGINS || '*';

// Configure CORS
app.use(cors({
    origin: CORS_ALLOWED_ORIGINS
}));

// Configure Socket.IO
const io = new Server(server, {
    cors: {
        origin: CORS_ALLOWED_ORIGINS
    }
});

app.use(express.json());

// Mock databases (same data as before)
const resourcesDb = [
    // ... copy all the resources_db data here ...
];

const projectsDb = [
    // ... copy all the projects_db data here ...
];

const allocationsDb = [
    // ... copy all the allocations_db data here ...
];

const notificationsDb = [];

// Projects routes
app.route('/projects')
    .get((req, res) => {
        const enhancedProjects = projectsDb.map(project => {
            const projectAllocations = allocationsDb
                .filter(alloc => alloc.projectId === project.id)
                .map(alloc => ({
                    ...alloc,
                    resourceDetails: resourcesDb.find(r => r.id === alloc.resourceId)
                }));

            return {
                ...project,
                resources: projectAllocations
            };
        });

        console.log("Enhanced Projects:", enhancedProjects); // Debug log
        res.json(enhancedProjects);
    })
    .post((req, res) => {
        const project = req.body;
        project.id = uuidv4();
        project.createdAt = new Date().toISOString();
        project.updatedAt = new Date().toISOString();

        const resources = project.resources || [];
        project.resources = [];
        projectsDb.push(project);

        // Create resource allocations
        resources.forEach(resource => {
            const allocation = {
                id: uuidv4(),
                resourceId: resource.resourceId,
                projectId: project.id,
                percentage: resource.percentage,
                startDate: project.startDate,
                endDate: project.endDate
            };
            allocationsDb.push(allocation);
            project.resources.push(allocation);
        });

        console.log("Created Project:", project); // Debug log
        res.status(201).json(project);
    })
    .put((req, res) => {
        const project = req.body;
        const index = projectsDb.findIndex(p => p.id === project.id);
        
        if (index !== -1) {
            projectsDb[index] = {
                ...projectsDb[index],
                phase: project.phase || projectsDb[index].phase,
                startDate: project.startDate || projectsDb[index].startDate,
                endDate: project.endDate || projectsDb[index].endDate,
                updatedAt: new Date().toISOString()
            };
            res.json(projectsDb[index]);
        } else {
            res.status(404).json({ error: 'Project not found' });
        }
    });

// Resources routes
app.route('/resources')
    .get((req, res) => {
        const enhancedResources = resourcesDb.map(resource => {
            const resourceAllocations = allocationsDb
                .filter(alloc => alloc.resourceId === resource.id)
                .map(alloc => ({
                    ...alloc,
                    projectDetails: projectsDb.find(p => p.id === alloc.projectId)
                }));

            return {
                ...resource,
                allocations: resourceAllocations
            };
        });
        res.json(enhancedResources);
    })
    .post((req, res) => {
        const resource = req.body;
        const newResource = {
            id: uuidv4(),
            name: resource.name,
            alias: resource.alias || '',
            role: resource.role,
            team: resource.team,
            availability: resource.availability || 100,
            createdAt: new Date().toISOString(),
            updatedAt: new Date().toISOString()
        };
        resourcesDb.push(newResource);
        res.status(201).json(newResource);
    });

// Start server
const PORT = process.env.PORT || 4000;
server.listen(PORT, () => {
    console.log(`Server is running on port ${PORT}`);
}); 